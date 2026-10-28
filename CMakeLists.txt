cmake_minimum_required(VERSION 3.21)
project(samsho VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# The neogeorecomp toolkit: the in-tree copy (a submodule in a clean
# checkout), or a checkout next to this project. The in-tree copy carries the
# generic v0.2.0 fixes (watchdog, bank guard, 4:3 fullscreen, M1 bank mask,
# audio output path).
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/neogeorecomp/CMakeLists.txt)
    set(ng_default ${CMAKE_CURRENT_SOURCE_DIR}/neogeorecomp)
else()
    set(ng_default ${CMAKE_CURRENT_SOURCE_DIR}/../neogeorecomp)
endif()
set(NEOGEORECOMP_DIR ${ng_default} CACHE PATH "neogeorecomp checkout")
add_subdirectory(${NEOGEORECOMP_DIR} neogeorecomp_build)

find_package(Python3 COMPONENTS Interpreter QUIET)

# Your unzipped MAME "samsho" set and "neogeo" system ROMs. The build reads
# them where they are; nothing derived from them is committed.
set(SAMSHO_ROM_DIR "" CACHE PATH "Directory with your samsho and Neo Geo BIOS ROM files")
# Optional: entry points a previous run found at runtime (--dump-misses).
set(SAMSHO_ENTRIES "${CMAKE_BINARY_DIR}/entries.txt" CACHE FILEPATH "Extra entry points for the recompiler")

# Stage 1: the generator.
add_executable(samsho_recomp src/recomp_main.c src/game.c)
target_link_libraries(samsho_recomp PRIVATE m68krecomp_core)
target_include_directories(samsho_recomp PRIVATE src)

# Stage 2: the player, with the generated C when ROMs are available.
set(GAME_SOURCES src/main.c)
set(GEN_DIR ${CMAKE_BINARY_DIR}/generated)
set(GEN_FILES 16)
if(SAMSHO_ROM_DIR)
    set(GEN_SOURCES ${GEN_DIR}/recomp_table.c)
    math(EXPR last "${GEN_FILES} - 1")
    foreach(i RANGE ${last})
        if(i LESS 10)
            list(APPEND GEN_SOURCES ${GEN_DIR}/recomp_0${i}.c)
        else()
            list(APPEND GEN_SOURCES ${GEN_DIR}/recomp_${i}.c)
        endif()
    endforeach()
    # The entry list starts empty; the `profile` target fills it from a
    # scripted play session and the next build regenerates with it.
    if(NOT EXISTS ${SAMSHO_ENTRIES})
        file(WRITE ${SAMSHO_ENTRIES} "")
    endif()
    file(MAKE_DIRECTORY ${GEN_DIR})
    add_custom_command(
        OUTPUT ${GEN_SOURCES} ${GEN_DIR}/recomp_common.h
        COMMAND samsho_recomp --rom-path ${SAMSHO_ROM_DIR} --out ${GEN_DIR} --files ${GEN_FILES}
                --entries ${SAMSHO_ENTRIES}
        DEPENDS samsho_recomp ${SAMSHO_ENTRIES}
        COMMENT "Recompiling Samurai Shodown from ${SAMSHO_ROM_DIR}")
    list(APPEND GAME_SOURCES ${GEN_SOURCES})
endif()

add_executable(samsho ${GAME_SOURCES} src/game.c)
if(WIN32)
    set_target_properties(samsho PROPERTIES OUTPUT_NAME "Samurai Shodown")
else()
    set_target_properties(samsho PROPERTIES OUTPUT_NAME "samsho")
endif()
target_link_libraries(samsho PRIVATE neogeorecomp)
target_include_directories(samsho PRIVATE src ${GEN_DIR})
if(SAMSHO_ROM_DIR)
    add_custom_target(profile
        COMMAND samsho --headless --rom-path ${SAMSHO_ROM_DIR} --frames 6000
                --dump-misses ${SAMSHO_ENTRIES}
        COMMAND samsho --headless --rom-path ${SAMSHO_ROM_DIR} --frames 19000
                --input ${CMAKE_CURRENT_SOURCE_DIR}/tests/play_long.txt
                --dump-misses ${SAMSHO_ENTRIES}
        DEPENDS samsho
        COMMENT "Profiling scripted sessions for runtime-only entry points")
    if(Python3_Interpreter_FOUND)
        add_custom_target(audio-check
            COMMAND samsho --headless --rom-path ${SAMSHO_ROM_DIR} --frames 12001
                    --input ${CMAKE_CURRENT_SOURCE_DIR}/tests/play_long.txt
                    --wav ${CMAKE_BINARY_DIR}/audio-check.wav
            COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/check_audio.py
                    ${CMAKE_BINARY_DIR}/audio-check.wav
            DEPENDS samsho
            COMMENT "Checking Samurai Shodown audio continuity")
    endif()
    target_compile_definitions(samsho PRIVATE SAMSHO_HAVE_RECOMP)
    if(MSVC)
        # Generated routines are large; /bigobj lifts the section limit.
        # /O1 avoids MSVC's superlinear optimizer blow-up on the giant
        # dispatch functions and still runs the 68000 code at full speed.
        set_source_files_properties(${GEN_SOURCES} PROPERTIES COMPILE_OPTIONS "/bigobj;/O1")
    else()
        # GCC/Clang at -O3 spend a long time on these giant switch functions.
        set_source_files_properties(${GEN_SOURCES} PROPERTIES COMPILE_OPTIONS "-O1")
    endif()
endif()
if(MSVC)
    target_compile_definitions(samsho PRIVATE _CRT_SECURE_NO_WARNINGS)
    target_compile_definitions(samsho_recomp PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

# Ship the SDL2 DLL (when the window is built) next to the executable.
if(WIN32 AND TARGET SDL2::SDL2)
    add_custom_command(TARGET samsho POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_RUNTIME_DLLS:samsho> $<TARGET_FILE_DIR:samsho>
        COMMAND_EXPAND_LISTS)
endif()
