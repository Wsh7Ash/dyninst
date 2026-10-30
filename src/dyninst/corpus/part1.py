"""Part 1 of the dyninst corpus: plan, attach, debug and intercept phases."""

from __future__ import annotations

from typing import Any

SKILLS: list[dict[str, Any]] = [
    {
        "slug": "plan-generate",
        "title": "Write an instrumentation plan before touching the target",
        "summary": "Declare the target, attachment method, probe points, emitter backend and cleanup step in one artifact that the rest of the run is checked against",
        "use_when": "you are about to instrument a process and no written plan exists yet",
        "avoid_when": "the engagement is a throwaway smoke test on a process you own and a plan would be pure overhead",
        "tags": ["plan", "design", "scope"],
        "steps": [
            "Name the target precisely: binary path, build id, PID or core file, and the host it runs on.",
            "Pick the attachment method that the target actually permits: Frida attach, GDB attach, LD_PRELOAD at launch, or an eBPF probe.",
            "List every probe point as a symbol plus an offset or line, not as a vague area of interest.",
            "Name the emitter that will produce the capture script and the retention rule for what it records.",
            "Write the teardown step, then sign and store the plan next to the evidence it will justify.",
        ],
        "signals": ["plan-committed", "attachment-selected", "probe-list-closed"],
        "patterns": [
            (
                "plan skeleton",
                "target: /opt/app/bin/server (build-id abc123)\nattachment: frida -p <pid>\nprobes:\n  - parse_header@libparse.so\n  - recv@libc.so.6\nemitter: frida-script\nteardown: session.detach() + signal handler restored\n",
            )
        ],
        "pitfalls": [
            "A plan written after the capture is a justification, not a plan; write it first and date it.",
            "Probe names that do not resolve against the loaded module waste the whole attachment window.",
        ],
        "done_when": [
            "The plan names a target, a method, every probe and a teardown.",
            "The plan is stored with the capture it produced.",
        ],
        "refs": [
            "[Frida JavaScript API](https://frida.re/docs/javascript-api/)",
            "[GDB documentation](https://sourceware.org/gdb/documentation/)",
        ],
        "meta": {"phase": "plan"},
    },
    {
        "slug": "plan-baseline-capture",
        "title": "Capture a clean baseline before instrumenting",
        "summary": "Record an uninstrumented run of the same input so every later observation has a control to compare against",
        "use_when": "you intend to claim that instrumented behaviour differs from normal behaviour",
        "avoid_when": "the target cannot be run twice, for example a one-shot crash on a live production host",
        "tags": ["plan", "baseline", "control"],
        "steps": [
            "Run the target with the exact input you will use under instrumentation, with no probes attached.",
            "Record exit code, wall time, stdout and stderr, plus any file or network side effects.",
            "Hash the inputs and outputs so the baseline is reproducible rather than remembered.",
            "Store the baseline next to the plan and reference it from every later finding.",
        ],
        "signals": ["baseline-run-complete", "baseline-hashed", "control-linked"],
        "patterns": [
            (
                "baseline capture",
                "python -m dyninst plan baseline --target ./server --input case01.bin --out baseline/",
            )
        ],
        "pitfalls": [
            "A baseline captured with different input proves nothing when compared to the instrumented run.",
            "Instrumentation that changes timing can make a benign race look like a new bug; the baseline must record timing.",
        ],
        "done_when": [
            "A baseline exists for the exact input under test and is hashed.",
            "Later captures cite the baseline identifier.",
        ],
        "refs": [
            "[Frida instrumentation overview](https://frida.re/docs/home/)",
        ],
        "meta": {"phase": "plan"},
    },
    {
        "slug": "plan-emitter-select",
        "title": "Choose the emitter that fits the target constraints",
        "summary": "Decide between a Frida script, a GDB macro file and an LD_PRELOAD library by checking what the target allows before writing any of them",
        "use_when": "several instrumentation backends are available and the wrong choice wastes the engagement window",
        "avoid_when": "the engagement mandates one backend, in which case the choice is already made for you",
        "tags": ["plan", "emitter", "constraints"],
        "steps": [
            "Check whether the target ships a Frida agent or permits ptrace; a hardened container may forbid both.",
            "Check whether the binary is static, stripped, or built without frame pointers, which changes what GDB can show.",
            "Check whether the process can be launched by you, which is the precondition for LD_PRELOAD.",
            "Record the rejected options and the reason, so a later reviewer can see the decision was constrained, not arbitrary.",
        ],
        "signals": ["constraints-recorded", "emitter-chosen", "rejections-documented"],
        "patterns": [
            (
                "constraint check",
                "cat /proc/sys/kernel/yama/ptrace_scope\nfile ./target | grep -E 'static|not stripped'\nldd ./target\n",
            )
        ],
        "pitfalls": [
            "Assuming ptrace works because it works on your workstation; check the actual host.",
            "Picking LD_PRELOAD for a statically linked binary, where it silently does nothing.",
        ],
        "done_when": [
            "One emitter is chosen with a recorded reason.",
            "Every rejected emitter has a recorded reason.",
        ],
        "refs": [
            "[Frida gadget and injection modes](https://frida.re/docs/modes/)",
            "[ld.so preload semantics](https://man7.org/linux/man-pages/man8/ld.so.8.html)",
        ],
        "meta": {"phase": "plan"},
    },
    {
        "slug": "plan-probe-map",
        "title": "Map probe points to real symbols before attaching",
        "summary": "Resolve every planned probe against the target's symbol tables so the attachment window is spent observing rather than debugging names",
        "use_when": "the probe list is written but its symbols have not been checked against the actual binary",
        "avoid_when": "the target is fully stripped and you have already accepted address-based probes instead of symbols",
        "tags": ["plan", "symbols", "recon"],
        "steps": [
            "Dump dynamic symbols with nm -D or readelf --dyn-syms and store the output as evidence.",
            "Match each planned probe against an exported or debug symbol and record its address and module.",
            "For probes that only exist in debug info, confirm the debug file or build-id link is reachable.",
            "Rewrite the plan with resolved addresses, and drop probes that cannot be resolved instead of hoping.",
        ],
        "signals": ["symbols-dumped", "probes-resolved", "unresolved-dropped"],
        "patterns": [
            (
                "symbol resolution",
                "readelf --dyn-syms -W ./libparse.so | grep -E 'FUNC.*(parse_header|parse_body)'\n",
            )
        ],
        "pitfalls": [
            "Resolving against the build host's library instead of the one actually loaded in the target.",
            "Trusting a stale symbol dump after the binary was rebuilt; rebuild invalidates every address.",
        ],
        "done_when": [
            "Every surviving probe maps to a symbol or address in the target.",
            "Dropped probes and their reasons are recorded.",
        ],
        "refs": [
            "[readelf manual](https://man7.org/linux/man-pages/man1/readelf.1.html)",
            "[Frida Module API](https://frida.re/docs/javascript-api/#module)",
        ],
        "meta": {"phase": "plan"},
    },
    {
        "slug": "frida-attach",
        "title": "Attach Frida to an already running process",
        "summary": "Connect to a live PID, confirm the session, load a script and prove the probe resolves before recording anything",
        "use_when": "the process is already running and you have permission and ptrace rights to instrument it",
        "avoid_when": "the process is protected by anti-debug or the host forbids ptrace for your user",
        "tags": ["frida", "attach", "live"],
        "steps": [
            "Confirm the PID is the process you mean to instrument, not a parent supervisor or a worker pool sibling.",
            "Attach with frida -p PID -l script.js and read the console for a session confirmation line.",
            "Resolve each probe with Module.findExportByName and log its address before installing any hook.",
            "Keep the session attached for the declared window, then detach explicitly and record the detach time.",
        ],
        "signals": ["session-established", "probe-resolved", "session-detached"],
        "patterns": [
            (
                "attach and resolve",
                "frida -p 4711 -l probes.js\n// probes.js\nconst addr = Module.findExportByName('libparse.so', 'parse_header');\nconsole.log('parse_header @', addr);\n",
            )
        ],
        "pitfalls": [
            "Attaching to a worker sibling instead of the process that handles the request under test.",
            "Leaving the session attached after the capture, which perturbs later measurements.",
        ],
        "done_when": [
            "The session is confirmed and every probe resolves to a non-null address.",
            "The detach is explicit and timestamped.",
        ],
        "refs": [
            "[Frida attach mode](https://frida.re/docs/modes/#attach)",
            "[Frida Module.findExportByName](https://frida.re/docs/javascript-api/#module-findexportbyname)",
        ],
        "meta": {"phase": "attach"},
    },
    {
        "slug": "frida-spawn",
        "title": "Spawn the target under Frida from the first instruction",
        "summary": "Start the process suspended under Frida so hooks are installed before the first user instruction runs, catching early-init bugs that attach misses",
        "use_when": "the bug you are chasing happens during startup, argument parsing or constructor execution",
        "avoid_when": "the target is already running with state you cannot recreate by respawning it",
        "tags": ["frida", "spawn", "startup"],
        "steps": [
            "Launch with frida -f ./target --no-pause=false and a script that resumes the process only after hooks are installed.",
            "Install every hook in the script body, then call Java.perform or resume the thread as appropriate.",
            "Pass the real argv through the spawn call so startup parsing sees the intended input.",
            "Record the spawned PID in the evidence bundle so the run can be tied to a process identity.",
        ],
        "signals": ["spawned-suspended", "hooks-installed-pre-entry", "process-resumed"],
        "patterns": [
            (
                "spawn with argv",
                "frida -f ./server -l startup.js --args --config ./conf.yml\n// startup.js installs hooks, then calls Process.resume()\n",
            )
        ],
        "pitfalls": [
            "Resuming before hooks are installed, which puts you back in the attach race you were trying to avoid.",
            "Forgetting that spawn gives the target a different environment than your shell, which changes startup paths.",
        ],
        "done_when": [
            "Hooks are installed before the first user instruction is observed.",
            "The spawned PID and argv are recorded with the capture.",
        ],
        "refs": [
            "[Frida spawn mode](https://frida.re/docs/modes/#spawn)",
            "[Frida Process.resume](https://frida.re/docs/javascript-api/#process-resume)",
        ],
        "meta": {"phase": "attach"},
    },
    {
        "slug": "gdb-attach",
        "title": "Attach GDB to a running process and stop it safely",
        "summary": "Take control of a live process with GDB, confirm the stop is the thread you expect and capture registers before changing any state",
        "use_when": "you need register-level inspection or a precise stop inside a running service",
        "avoid_when": "the process must not be paused, for example a latency-sensitive production endpoint",
        "tags": ["gdb", "attach", "ptrace"],
        "steps": [
            "Attach with gdb -p PID and confirm GDB reports the stop and the loaded shared libraries.",
            "Run info threads and confirm which thread stopped; select the thread that serves the request under test.",
            "Capture info registers, bt and the current instruction pointer before setting any breakpoint.",
            "Detach with detach rather than quit so the process continues instead of being killed.",
        ],
        "signals": ["attached-and-stopped", "thread-identified", "registers-captured"],
        "patterns": [
            (
                "attach and inspect",
                "gdb -p 4711 -batch -ex 'info threads' -ex 'info registers' -ex 'bt' -ex 'detach'\n",
            )
        ],
        "pitfalls": [
            "Quitting GDB instead of detaching kills the instrumented process and destroys the bug site.",
            "Inpecting a worker thread that never handles the request you are testing.",
        ],
        "done_when": [
            "A thread is identified and its registers and backtrace are captured.",
            "The process is detached and still running afterwards.",
        ],
        "refs": [
            "[GDB attach to a process](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Attach.html)",
        ],
        "meta": {"phase": "attach"},
    },
    {
        "slug": "ldpreload-launch",
        "title": "Launch a target with an LD_PRELOAD interposer",
        "summary": "Start the process yourself with a preload library so interception is in place before the first call, and prove the library actually loaded",
        "use_when": "you control how the target is launched and need interception without an external debugger",
        "avoid_when": "the target is statically linked, setuid, or already running",
        "tags": ["ldpreload", "launch", "interposition"],
        "steps": [
            "Build the interposer as a shared object with -shared -fPIC and record its hash.",
            "Launch with LD_PRELOAD=./hook.so ./target and pass the real arguments through.",
            "Prove the library loaded by logging from a constructor or by reading /proc/PID/maps for the .so path.",
            "Record the environment the process actually saw, including the full LD_PRELOAD value.",
        ],
        "signals": ["interposer-built", "library-observed-in-maps", "constructor-ran"],
        "patterns": [
            (
                "preload launch",
                "gcc -shared -fPIC -o hook.so hook.c -ldl\nLD_PRELOAD=./hook.so ./target --input case01.bin\n",
            )
        ],
        "pitfalls": [
            "setuid binaries ignore LD_PRELOAD, so a successful launch proves nothing about interception.",
            "A relative LD_PRELOAD path breaks after the process changes directory; use an absolute path.",
        ],
        "done_when": [
            "The library appears in the process maps and its constructor ran.",
            "The exact LD_PRELOAD value is recorded with the capture.",
        ],
        "refs": [
            "[ld.so preload](https://man7.org/linux/man-pages/man8/ld.so.8.html)",
            "[dlsym RTLD_NEXT](https://man7.org/linux/man-pages/man3/dlsym.3.html)",
        ],
        "meta": {"phase": "attach"},
    },
    {
        "slug": "gdb-breakpoint",
        "title": "Stop execution at a function with a GDB breakpoint",
        "summary": "Halt at a chosen function or line and capture registers, arguments and the call stack at the exact moment the code runs",
        "use_when": "you need to inspect state at a known point and the program can tolerate being paused",
        "avoid_when": "the function is called at a rate where a breakpoint per call would stall the target",
        "tags": ["gdb", "breakpoint", "stop"],
        "steps": [
            "Set the breakpoint by symbol, file:line, or address, preferring symbol plus offset.",
            "Run or continue until the breakpoint reports a stop, and confirm the stopped frame is the one you asked for.",
            "Capture info args, info locals, info registers and bt before stepping anywhere.",
            "Delete the breakpoint or continue, and record how many times it was hit.",
        ],
        "signals": ["breakpoint-set", "stop-confirmed", "state-captured"],
        "patterns": [
            (
                "break and capture",
                "gdb -q ./target -batch -ex 'break parse_header' -ex 'run' -ex 'info args' -ex 'bt 5'\n",
            )
        ],
        "pitfalls": [
            "A breakpoint on an inlined function may never report a stop, because there is no call to break on.",
            "With optimisation on, info args and info locals can be optimised out entirely.",
        ],
        "done_when": [
            "The stop is confirmed on the intended frame.",
            "Arguments, locals and backtrace are captured as evidence.",
        ],
        "refs": [
            "[GDB breakpoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Breakpoints.html)",
        ],
        "meta": {"phase": "debug"},
    },
    {
        "slug": "gdb-watchpoint",
        "title": "Catch a write to memory with a GDB watchpoint",
        "summary": "Trap the exact instruction that mutates a field or buffer so you can attribute an unexpected value to the writer instead of guessing",
        "use_when": "a value changes unexpectedly and you need the writing instruction, not just the bad value",
        "avoid_when": "the watched region is written on every iteration, which makes the watchpoint unusable",
        "tags": ["gdb", "watchpoint", "memory"],
        "steps": [
            "Resolve the address of the field or buffer with print &obj.field, and note the byte width.",
            "Set a watchpoint on that address with watch *(int*)0xADDR sized to the field.",
            "Continue and capture the stack at the stop, which is the writer you were looking for.",
            "Remove the watchpoint and record the writer's frame, function and source line.",
        ],
        "signals": ["watchpoint-armed", "write-caught", "writer-frame-captured"],
        "patterns": [
            (
                "hardware watchpoint",
                "watch *(unsigned int*)0x7fffffffe2a0\ncontinue\nbt\n",
            )
        ],
        "pitfalls": [
            "Watching a stack address across a function return, after which the address refers to unrelated data.",
            "Software watchpoints are extremely slow; prefer hardware watchpoints where they are available.",
        ],
        "done_when": [
            "The writing instruction is identified with a stack and source line.",
            "The watchpoint is removed before the run continues.",
        ],
        "refs": [
            "[GDB watchpoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Set-Watchpoints.html)",
        ],
        "meta": {"phase": "debug"},
    },
    {
        "slug": "gdb-stepi",
        "title": "Single-step instructions to follow a branch precisely",
        "summary": "Advance one machine instruction at a time around a suspicious branch so the observed path is the path you report, not an approximation",
        "use_when": "source stepping jumps over the interesting branch or the code has no debug info",
        "avoid_when": "the region is thousands of instructions long or inside a tight loop with no exit condition",
        "tags": ["gdb", "stepi", "branch"],
        "steps": [
            "Stop at the branch instruction and record its address, mnemonic and current flags.",
            "Step one instruction at a time with stepi, logging the program counter and flags after each step.",
            "Stop at the first deviation from the expected path and capture the registers that decided it.",
            "Write down the branch decision as address, condition and observed flag values.",
        ],
        "signals": ["branch-address-recorded", "single-step-trace", "divergence-captured"],
        "patterns": [
            (
                "step loop",
                "gdb -q ./target -batch -ex 'break *0x4011a0' -ex 'run' -ex 'x/3i $pc' -ex 'stepi' -ex 'info registers eflags'\n",
            )
        ],
        "pitfalls": [
            "Stepping into a syscall instruction can move you into the kernel and lose the user-space context.",
            "A branch whose flags were set far earlier will not show the cause at the branch itself; capture backwards too.",
        ],
        "done_when": [
            "The branch address, condition and observed flags are recorded.",
            "The divergence point is tied to a register value.",
        ],
        "refs": [
            "[GDB stepping](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Continuing-and-Stepping.html)",
        ],
        "meta": {"phase": "debug"},
    },
    {
        "slug": "gdb-break-condition",
        "title": "Break only on the call you care about",
        "summary": "Attach a condition to a breakpoint so a high-frequency function stops on the triggering argument instead of thousands of benign calls",
        "use_when": "the target function is called constantly and only one call shape matters",
        "avoid_when": "the distinguishing value is not available in a form GDB can evaluate at the breakpoint",
        "tags": ["gdb", "conditional", "filter"],
        "steps": [
            "Set the breakpoint normally and let it hit once to learn the argument layout.",
            "Add a condition that matches the triggering shape, for example length > 512 or a magic header value.",
            "Confirm the condition evaluates without errors by printing it at a stop.",
            "Record the condition text with the capture so the filter is reproducible.",
        ],
        "signals": ["condition-set", "condition-evaluates", "targeted-stop"],
        "patterns": [
            (
                "conditional break",
                "break parse_header if len > 512\ncondition 1 strcmp(header, \"MAGIC\") == 0\n",
            )
        ],
        "pitfalls": [
            "A condition that calls a function can change program state or crash inside GDB.",
            "Conditions evaluate slowly; a condition on a hot function can still stall the target.",
        ],
        "done_when": [
            "The breakpoint stops only on the intended call shape.",
            "The condition text is recorded with the capture.",
        ],
        "refs": [
            "[GDB conditions](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Conditions.html)",
        ],
        "meta": {"phase": "debug"},
    },
    {
        "slug": "ldpreload-hook",
        "title": "Interpose a libc function with an LD_PRELOAD hook",
        "summary": "Override a library call, forward to the real implementation with dlsym RTLD_NEXT, and log or mutate arguments without breaking the process",
        "use_when": "you need to observe or alter a library call and you control process launch",
        "avoid_when": "the call is resolved internally by the binary, for example a statically linked helper",
        "tags": ["ldpreload", "hook", "libc"],
        "steps": [
            "Declare a function with the same signature as the target symbol and resolve the original with dlsym(RTLD_NEXT, name).",
            "Log the arguments before forwarding, using a write-safe path that cannot recurse into the hook.",
            "Forward to the original, then log the return value and errno.",
            "Guard re-entrancy with a thread-local flag so a log call cannot call the hooked function again.",
        ],
        "signals": ["original-resolved", "args-logged", "return-logged"],
        "patterns": [
            (
                "interpose write",
                "static ssize_t (*real_write)(int, const void *, size_t);\nssize_t write(int fd, const void *buf, size_t n) {\n  if (!real_write) real_write = dlsym(RTLD_NEXT, \"write\");\n  log_call(fd, n);\n  return real_write(fd, buf, n);\n}\n",
            )
        ],
        "pitfalls": [
            "Logging with printf inside a hook for write causes infinite recursion; use write directly with a recursion guard.",
            "Symbol versioning can make dlsym return the wrong implementation for versioned symbols.",
        ],
        "done_when": [
            "The original is resolved and every call is forwarded.",
            "The process completes without recursion or crashes.",
        ],
        "refs": [
            "[dlsym RTLD_NEXT](https://man7.org/linux/man-pages/man3/dlsym.3.html)",
            "[LD_PRELOAD hooks](https://man7.org/linux/man-pages/man8/ld.so.8.html)",
        ],
        "meta": {"phase": "intercept"},
    },
    {
        "slug": "ldpreload-constructor",
        "title": "Run setup code before main with a constructor",
        "summary": "Use an attribute constructor to install hooks, read configuration and open a log before the target's own initialisation runs",
        "use_when": "the behaviour you need to observe happens in constructors or before main",
        "avoid_when": "the process's own constructors must run first because your setup depends on their state",
        "tags": ["ldpreload", "constructor", "startup"],
        "steps": [
            "Mark the setup function with __attribute__((constructor)) and keep it free of allocations that may not be ready yet.",
            "Open the log with a raw open and write descriptor rather than stdio, which may not be initialised.",
            "Record the process start time and the preload library path from the constructor.",
            "Flush and close in a destructor marked __attribute__((destructor)).",
        ],
        "signals": ["constructor-ran", "log-opened-early", "destructor-flushed"],
        "patterns": [
            (
                "constructor",
                "__attribute__((constructor)) static void setup(void) {\n  log_fd = open(\"/tmp/hook.log\", O_WRONLY | O_CREAT | O_APPEND, 0600);\n}\n",
            )
        ],
        "pitfalls": [
            "Calling malloc or stdio in a constructor can deadlock before the allocator or stdio is initialised.",
            "Constructor order across libraries is not guaranteed, so do not depend on another preload library's setup.",
        ],
        "done_when": [
            "The constructor runs and the log is opened before main.",
            "A destructor flushes and closes the log.",
        ],
        "refs": [
            "[GCC function attributes](https://gcc.gnu.org/onlinedocs/gcc/Function-Attributes.html)",
        ],
        "meta": {"phase": "intercept"},
    },
    {
        "slug": "ldpreload-syscall",
        "title": "Intercept a syscall wrapper rather than raw system calls",
        "summary": "Hook the libc wrapper so both direct calls and library callers are covered, and know exactly which paths the hook cannot see",
        "use_when": "you need to observe file, network or process syscalls from a dynamically linked target",
        "avoid_when": "the target issues raw syscalls with inline assembly, which bypasses libc entirely",
        "tags": ["ldpreload", "syscall", "coverage"],
        "steps": [
            "Identify the libc wrapper for the syscall, for example open, openat, connect or execve.",
            "Interpose the wrapper and forward with dlsym RTLD_NEXT, recording arguments and the returned errno.",
            "Note that Go binaries and some hardened runtimes issue raw syscalls that never reach the wrapper.",
            "Cross-check coverage against strace for the same run and explain any syscall the hook missed.",
        ],
        "signals": ["wrapper-hooked", "calls-recorded", "coverage-compared"],
        "patterns": [
            (
                "interpose openat",
                "int openat(int dirfd, const char *path, int flags, ...) {\n  va_list ap; va_start(ap, flags);\n  mode_t mode = va_arg(ap, mode_t); va_end(ap);\n  syslog_call(path, flags);\n  return real_openat(dirfd, path, flags, mode);\n}\n",
            )
        ],
        "pitfalls": [
            "Reading a variadic argument unconditionally passes garbage when the flag does not include O_CREAT.",
            "Reporting full syscall coverage when the target uses raw syscalls is a false claim; verify against strace.",
        ],
        "done_when": [
            "The wrapper hook is installed and forwards correctly for both variadic and fixed calls.",
            "Coverage is compared against an independent tracer.",
        ],
        "refs": [
            "[openat(2)](https://man7.org/linux/man-pages/man2/openat.2.html)",
            "[strace](https://strace.io/)",
        ],
        "meta": {"phase": "intercept"},
    },
    {
        "slug": "frida-hook-native",
        "title": "Replace a native function with Frida Interceptor",
        "summary": "Install onEnter and onLeave hooks on an exported native function and capture arguments, return value and caller, then restore the original",
        "use_when": "you need argument and return visibility without stopping the process",
        "avoid_when": "the function is called on a hot path where per-call JavaScript would change behaviour",
        "tags": ["frida", "interceptor", "native"],
        "steps": [
            "Resolve the export with Module.findExportByName and assert it is not null before attaching.",
            "Attach with onEnter and onLeave, reading arguments with the declared signature rather than guessing types.",
            "Read the return value in onLeave with retval and record the caller from this.returnAddress.",
            "Call listener.detach() at the end of the window and confirm no hooks remain.",
        ],
        "signals": ["export-resolved", "onenter-fired", "detached-clean"],
        "patterns": [
            (
                "native hook",
                "const p = Module.findExportByName('libparse.so', 'parse_header');\nInterceptor.attach(p, {\n  onEnter(args) { send({ev: 'enter', len: args[1].toInt32()}); },\n  onLeave(ret) { send({ev: 'leave', ret: ret.toInt32()}); }\n});\n",
            )
        ],
        "pitfalls": [
            "Reading a pointer argument as a string without bounding the read can crash on unterminated buffers.",
            "Hooking an export that is also called by the hook's own logging path creates recursion.",
        ],
        "done_when": [
            "Enter and leave events are captured with typed arguments.",
            "The listener is detached and the target is unmodified afterwards.",
        ],
        "refs": [
            "[Frida Interceptor](https://frida.re/docs/javascript-api/#interceptor)",
        ],
        "meta": {"phase": "intercept"},
    },
    {
        "slug": "frida-java-hook",
        "title": "Hook a Java method with Frida on Android",
        "summary": "Attach to a Java method through the runtime's reflection layer and capture arguments and return values without patching the APK",
        "use_when": "the app is Java or Kotlin running on ART and you have a debuggable or rooted target",
        "avoid_when": "the method is inlined or the app uses a hardened runtime that blocks Frida",
        "tags": ["frida", "java", "android"],
        "steps": [
            "Wrap the hook in Java.perform so it runs after the VM is ready.",
            "Use Java.use on the class name and override the method with an implementation that calls this.method.overload(...).call(this, args).",
            "Log arguments and return value, then return the original result unchanged unless mutation is the goal.",
            "Keep a reference to the implementation so it can be reverted, and confirm the class was not loaded twice.",
        ],
        "signals": ["java-perform-ran", "method-wrapped", "result-returned"],
        "patterns": [
            (
                "java hook",
                "Java.perform(function () {\n  const C = Java.use('com.example.Api');\n  C.login.implementation = function (u, p) {\n    send({u: u, plen: p.length});\n    return this.login(u, p);\n  };\n});\n",
            )
        ],
        "pitfalls": [
            "Overloading resolution fails when the signature is ambiguous; use .overload with explicit types.",
            "Hooking before the class is loaded throws; retry after the class loader has run.",
        ],
        "done_when": [
            "The method wrapper fires on a real call with typed arguments.",
            "The original behaviour is preserved unless mutation was intended.",
        ],
        "refs": [
            "[Frida Java API](https://frida.re/docs/javascript-api/#java)",
        ],
        "meta": {"phase": "intercept"},
    },
]