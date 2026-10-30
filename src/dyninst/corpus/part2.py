"""Part 2 of the dyninst corpus: trace, kernel, post-mortem, signal, capture."""

from __future__ import annotations

from typing import Any

SKILLS: list[dict[str, Any]] = [
    {
        "slug": "probe-function-entry",
        "title": "Observe function entry with typed arguments",
        "summary": "Record arguments at entry with their declared types so a later claim about what reached the function is backed by observed values",
        "use_when": "you need to prove which input reached a function rather than inferring it from output",
        "avoid_when": "the function is called so often that per-call capture changes the timing you are measuring",
        "tags": ["trace", "entry", "arguments"],
        "steps": [
            "Resolve the symbol and select the calling convention so argument registers are read correctly.",
            "Decode each argument with its declared type: integer width, pointer plus bounds, or struct layout.",
            "Bound every pointer read and record the actual length read alongside the value.",
            "Emit one record per entry with a monotonically increasing sequence number.",
        ],
        "signals": ["entry-observed", "args-typed", "sequence-contiguous"],
        "patterns": [
            (
                "entry record",
                "Interceptor.attach(addr, {\n  onEnter(args) {\n    const len = args[1].toInt32();\n    send({seq: ++n, len: len, buf: len > 0 && len < 4096 ? args[0].readUtf8(len) : null});\n  }\n});\n",
            )
        ],
        "pitfalls": [
            "Reading a pointer as a C string when the callee takes a length can run past the buffer and crash.",
            "Capturing only the first call hides the interesting call in a batch; keep a sequence counter.",
        ],
        "done_when": [
            "Entries are recorded with typed arguments and bounded reads.",
            "The sequence numbering shows no gaps in the captured window.",
        ],
        "refs": [
            "[Frida NativePointer](https://frida.re/docs/javascript-api/#nativepointer)",
        ],
        "meta": {"phase": "trace"},
    },
    {
        "slug": "probe-function-return",
        "title": "Observe function return and error paths",
        "summary": "Capture the return value and the error branch so a claim about failure handling is backed by the value the function actually returned",
        "use_when": "success and failure are distinguished by a return code or an out-parameter",
        "avoid_when": "the function returns through multiple epilogues that the hook does not cover",
        "tags": ["trace", "return", "errors"],
        "steps": [
            "Hook onLeave and read retval with the declared return type rather than as a raw integer.",
            "For out-parameter style APIs, read the output struct in onLeave after the callee has filled it.",
            "Record errno or the last-error value immediately on leave, before any other call can clobber it.",
            "Pair the record with its entry sequence number so return values are matched to the right call.",
        ],
        "signals": ["return-observed", "errno-captured", "call-paired"],
        "patterns": [
            (
                "return record",
                "Interceptor.attach(addr, {\n  onEnter() { this.seq = ++n; },\n  onLeave(ret) { send({seq: this.seq, ret: ret.toInt32(), err: errnoValue()}); }\n});\n",
            )
        ],
        "pitfalls": [
            "Reading errno after another libc call in the hook has already overwritten it.",
            "A function with an early return and a normal return can look identical if only the value is captured, not the epilogue address.",
        ],
        "done_when": [
            "Return values and error codes are captured per call.",
            "Each return record pairs with exactly one entry record.",
        ],
        "refs": [
            "[Frida onLeave](https://frida.re/docs/javascript-api/#interceptor-attach)",
        ],
        "meta": {"phase": "trace"},
    },
    {
        "slug": "probe-multi-entry",
        "title": "Trace several functions as one ordered timeline",
        "summary": "Hook a set of related functions and merge their events into a single sequence so ordering between them is visible instead of guessed",
        "use_when": "a bug depends on the order in which several functions run, not on any single one",
        "avoid_when": "the functions run on multiple threads and a total order would be fabricated rather than measured",
        "tags": ["trace", "timeline", "ordering"],
        "steps": [
            "Declare the probe set with a stable name per function and one shared sequence counter.",
            "Install every hook before resuming the process so the first call is not missed.",
            "Record thread id with each event so cross-thread ordering is not invented.",
            "Sort by sequence within a thread and by timestamp across threads, and state which ordering the report uses.",
        ],
        "signals": ["probe-set-installed", "events-merged", "threads-separated"],
        "patterns": [
            (
                "multi-probe",
                "const probes = {parse_header: a1, parse_body: a2, dispatch: a3};\nfor (const [name, addr] of Object.entries(probes)) {\n  Interceptor.attach(addr, { onEnter() { send({seq: ++n, fn: name, tid: tid()}); } });\n}\n",
            )
        ],
        "pitfalls": [
            "Interleaving events from several threads into one list and presenting it as a causal order.",
            "Installing probes one at a time after the process runs, so the earliest calls never appear.",
        ],
        "done_when": [
            "Every probe in the set is installed before execution.",
            "Events carry a thread id and the ordering rule is stated.",
        ],
        "refs": [
            "[Frida ThreadId](https://frida.re/docs/javascript-api/#process-getcurrentthreadid)",
        ],
        "meta": {"phase": "trace"},
    },
    {
        "slug": "frida-stalker-trace",
        "title": "Trace executed code with Frida Stalker",
        "summary": "Follow a thread's real instruction stream to see which basic blocks executed, without setting a breakpoint on every one",
        "use_when": "you need coverage of an unknown code path rather than a check at known symbols",
        "avoid_when": "the target is timing sensitive, because Stalker slows execution by an order of magnitude",
        "tags": ["frida", "stalker", "coverage"],
        "steps": [
            "Follow the thread of interest with Stalker.follow and a transform that records block entry addresses.",
            "Keep the transform minimal: append a call to a logging stub rather than inlining heavy JavaScript.",
            "Store block addresses in a set and resolve them to symbols after the run, not inside the transform.",
            "Unfollow the thread and stop the Stalker session before doing any analysis.",
        ],
        "signals": ["stalker-following", "blocks-recorded", "unfollowed"],
        "patterns": [
            (
                "stalker follow",
                "const blocks = new Set();\nStalker.follow(tid, {\n  transform(iterator) {\n    let ins;\n    while ((ins = iterator.next()) !== null) {\n      if (ins.address in seen) continue;\n      blocks.add(ins.address);\n    }\n  }\n});\n",
            )
        ],
        "pitfalls": [
            "Doing heavy work inside the transform turns a slow trace into a hung process.",
            "Following every thread at once produces an unusable interleaving; follow one and say which.",
        ],
        "done_when": [
            "Executed blocks are recorded for one named thread.",
            "Stalker is unfollowed and the process returns to normal speed.",
        ],
        "refs": [
            "[Frida Stalker](https://frida.re/docs/javascript-api/#stalker)",
        ],
        "meta": {"phase": "trace"},
    },
    {
        "slug": "gdb-tracepoints",
        "title": "Collect data with GDB tracepoints instead of stopping",
        "summary": "Sample values at chosen points without halting the program, then read the trace buffer back, which suits hot paths a breakpoint cannot survive",
        "use_when": "a breakpoint per hit would stall the target but you still need values from those points",
        "avoid_when": "the trace buffer would wrap before the interesting event occurs",
        "tags": ["gdb", "tracepoint", "sampling"],
        "steps": [
            "Create a tracepoint at the address with trace, and attach actions that save only the values you need.",
            "Size the trace buffer for the expected event count, or accept wrapping and record that it wrapped.",
            "Run the program, then inspect collected samples with tfind and tdump.",
            "Export the samples and state the sampling window, because a tracepoint set is not a complete log.",
        ],
        "signals": ["tracepoint-created", "samples-collected", "window-stated"],
        "patterns": [
            (
                "tracepoint",
                "gdb -q ./target -batch -ex 'trace parse_header' -ex 'actions' -ex 'collect $rdi, $rsi' -ex 'end' -ex 'tstart' -ex 'run' -ex 'tstop' -ex 'tdump'\n",
            )
        ],
        "pitfalls": [
            "Presenting tracepoint samples as a complete record of every call, when the buffer may have wrapped.",
            "Collecting large memory regions at a hot tracepoint fills the buffer almost immediately.",
        ],
        "done_when": [
            "Samples are collected and exported with the sampling window stated.",
            "Buffer wrapping is recorded if it happened.",
        ],
        "refs": [
            "[GDB tracepoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Tracepoints.html)",
        ],
        "meta": {"phase": "trace"},
    },
    {
        "slug": "ebpf-kprobe",
        "title": "Attach an eBPF kprobe to a kernel function",
        "summary": "Observe kernel-side function entry with a kprobe and read the arguments from the register context, without loading a kernel module",
        "use_when": "the behaviour you need is inside the kernel and user-space hooks cannot see it",
        "avoid_when": "the kernel is built without BTF or the symbol you need is inlined and has no probe point",
        "tags": ["ebpf", "kprobe", "kernel"],
        "steps": [
            "Confirm the target symbol exists in /proc/kallsyms and is not inlined away.",
            "Attach a kprobe with bpftrace or a small BCC program and read arguments from the pt_regs context.",
            "Bound every kernel memory read with bpf_probe_read_user or bpf_probe_read_kernel and check the return.",
            "Detach the probe and verify with bpftool that no program remains attached.",
        ],
        "signals": ["symbol-present", "kprobe-attached", "probe-detached"],
        "patterns": [
            (
                "kprobe one-liner",
                "bpftrace -e 'kprobe:vfs_open { printf(\"%s %d\\n\", comm, pid); }'\n",
            )
        ],
        "pitfalls": [
            "Dereferencing kernel pointers directly in the probe fails; use the bounded read helpers.",
            "A kprobe on an inlined or renamed symbol never fires, which looks identical to a quiet system.",
        ],
        "done_when": [
            "The probe fires on a real event and arguments are captured.",
            "bpftool confirms no program is left attached.",
        ],
        "refs": [
            "[bpftrace kprobes](https://bpftrace.org/)",
            "[BPF helpers](https://docs.kernel.org/bpf/helper-bpf-probe-read-kernel.html)",
        ],
        "meta": {"phase": "kernel"},
    },
    {
        "slug": "ebpf-uprobe",
        "title": "Attach an eBPF uprobe to a user-space function",
        "summary": "Probe a function inside a specific binary from the kernel side, which works when attaching a debugger to the process is not permitted",
        "use_when": "ptrace is restricted but the kernel permits uprobes on the target binary",
        "avoid_when": "the target binary is replaced frequently, because uprobes are bound to an inode and offset",
        "tags": ["ebpf", "uprobe", "user-space"],
        "steps": [
            "Resolve the symbol offset in the on-disk binary, since the probe binds to a file offset, not a runtime address.",
            "Attach the uprobe with the full path to the binary so the probe binds to the right inode.",
            "Read user-space strings with bpf_probe_read_user_str and check the truncated length.",
            "Detach and confirm removal, then record the binary hash the probe was bound to.",
        ],
        "signals": ["offset-resolved", "uprobe-attached", "binary-hashed"],
        "patterns": [
            (
                "uprobe attach",
                "bpftrace -e 'uprobe:/opt/app/bin/server:parse_header { printf(\"%s\\n\", str(arg1)); }'\n",
            )
        ],
        "pitfalls": [
            "Binding to a symlink or a relative path can attach to the wrong inode after an upgrade.",
            "User-space reads from an unmapped page return an error; treat zero-length results as a read failure, not an empty string.",
        ],
        "done_when": [
            "The probe fires on a real call in the named binary.",
            "The binary hash and probe offset are recorded.",
        ],
        "refs": [
            "[bpftrace uprobes](https://bpftrace.org/)",
        ],
        "meta": {"phase": "kernel"},
    },
    {
        "slug": "ebpf-tracepoint",
        "title": "Use a stable tracepoint instead of a raw kprobe",
        "summary": "Attach to a documented tracepoint whose ABI the kernel maintains, so the probe does not break when internal function signatures change",
        "use_when": "a tracepoint exists for the event you care about and you want a probe that survives kernel updates",
        "avoid_when": "no tracepoint covers the event and only an internal function does",
        "tags": ["ebpf", "tracepoint", "stability"],
        "steps": [
            "List available tracepoints from /sys/kernel/tracing/events and choose the one matching the event.",
            "Read the tracepoint's format file to learn the field offsets the probe will read.",
            "Attach and read only the documented fields rather than poking at adjacent memory.",
            "Record the kernel version and tracepoint name so the capture can be reproduced.",
        ],
        "signals": ["tracepoint-selected", "format-read", "kernel-version-recorded"],
        "patterns": [
            (
                "tracepoint attach",
                "bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf(\"%s %s\\n\", comm, str(args.filename)); }'\n",
            )
        ],
        "pitfalls": [
            "Reading a field that the format file marks as a different type produces plausible garbage.",
            "Assuming tracepoint field offsets are stable across kernel versions; re-read the format file per host.",
        ],
        "done_when": [
            "The tracepoint fires and documented fields are read correctly.",
            "Kernel version and tracepoint name are recorded.",
        ],
        "refs": [
            "[tracefs events](https://docs.kernel.org/trace/events.html)",
        ],
        "meta": {"phase": "kernel"},
    },
    {
        "slug": "core-dump-analyze",
        "title": "Analyse a core dump for the crashing instruction",
        "summary": "Open a core file with the matching binary, identify the faulting frame and capture the state that supports the crash claim",
        "use_when": "the process already crashed and a core file was preserved",
        "avoid_when": "the core was produced from a different build than the binary you have",
        "tags": ["post-mortem", "core", "crash"],
        "steps": [
            "Confirm the core matches the binary by build-id or by a recorded checksum before opening it.",
            "Load with gdb ./binary core and capture bt, info registers and the faulting instruction.",
            "Identify the fault type from the signal and the faulting address, and record both.",
            "Save the GDB session transcript as the evidence rather than a retyped summary.",
        ],
        "signals": ["core-matched", "fault-frame-captured", "transcript-saved"],
        "patterns": [
            (
                "core analysis",
                "gdb -q ./server core.4711 -batch -ex 'bt 20' -ex 'info registers' -ex 'x/4i $pc' -ex 'info signal SIGSEGV'\n",
            )
        ],
        "pitfalls": [
            "Analysing a core against a rebuilt binary produces a confident but wrong backtrace.",
            "Optimised builds can lose the innermost frame, so state that rather than inventing a caller.",
        ],
        "done_when": [
            "The core is proven to match the binary and the faulting frame is captured.",
            "The transcript is stored with the finding.",
        ],
        "refs": [
            "[GDB core files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Core-File-Generation.html)",
        ],
        "meta": {"phase": "post-mortem"},
    },
    {
        "slug": "gdb-frame-capture",
        "title": "Capture a backtrace that survives review",
        "summary": "Record a backtrace with frame arguments and source lines so a reviewer can follow the same path without re-running the crash",
        "use_when": "the backtrace is the main evidence for a reachability claim",
        "avoid_when": "the stack is corrupted, in which case say so instead of presenting a plausible-looking trace",
        "tags": ["post-mortem", "backtrace", "evidence"],
        "steps": [
            "Capture bt full so frame arguments and locals are included with each frame.",
            "Check for frames marked as corrupted or as question marks and record them as unknown rather than dropping them.",
            "Resolve each frame to a function plus file and line where debug info allows.",
            "Save the raw backtrace text, not a reformatted table, so it can be compared later.",
        ],
        "signals": ["backtrace-captured", "corruption-checked", "frames-resolved"],
        "patterns": [
            (
                "full backtrace",
                "gdb -q ./server core -batch -ex 'set print frame-arguments all' -ex 'bt full'\n",
            )
        ],
        "pitfalls": [
            "A corrupted stack can produce a confident chain of frames that never ran.",
            "Trimming frames to make a path look shorter is misrepresentation; keep every frame and mark unknowns.",
        ],
        "done_when": [
            "A full backtrace is saved with arguments and unknowns marked.",
            "Every frame is either resolved or explicitly marked unresolved.",
        ],
        "refs": [
            "[GDB backtrace](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Backtrace.html)",
        ],
        "meta": {"phase": "post-mortem"},
    },
    {
        "slug": "crash-signal-decode",
        "title": "Decode the crash signal and faulting address",
        "summary": "Turn SI_CODE, the faulting address and the signal number into a precise fault classification instead of calling everything a segfault",
        "use_when": "you need to distinguish a null dereference from a wild pointer, a stack overflow or a deliberate abort",
        "avoid_when": "the signal was delivered by another thread or by raise rather than by the faulting instruction",
        "tags": ["post-mortem", "signal", "classification"],
        "steps": [
            "Read the signal number and si_code from the siginfo structure, which distinguishes SEGV_MAPERR from SEGV_ACCERR.",
            "Record the faulting address from si_addr and compare it to the mapping that should have contained it.",
            "Check whether the faulting instruction is a load, store or execute, since the classification depends on it.",
            "Write the classification as a sentence with the evidence, for example a read of an unmapped address.",
        ],
        "signals": ["siginfo-read", "fault-classified", "mapping-compared"],
        "patterns": [
            (
                "siginfo decode",
                "gdb -q ./server core -batch -ex 'p $_siginfo' -ex 'p $_siginfo.si_code' -ex 'p $_siginfo._sifields._sigfault.si_addr'\n",
            )
        ],
        "pitfalls": [
            "Calling every SIGSEGV a null dereference when si_addr is non-zero and points into an unmapped region.",
            "Ignoring SIGABRT, which is a deliberate abort and not a memory fault at all.",
        ],
        "done_when": [
            "The signal, si_code and faulting address are recorded together.",
            "The classification names the access type and the mapping state.",
        ],
        "refs": [
            "[signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html)",
            "[sigaction(2)](https://man7.org/linux/man-pages/man2/sigaction.2.html)",
        ],
        "meta": {"phase": "post-mortem"},
    },
    {
        "slug": "frida-post-mortem-core",
        "title": "Capture a Frida snapshot before the process is torn down",
        "summary": "Dump module ranges and thread state from a live Frida session so a later crash can be tied to the exact loaded layout it ran under",
        "use_when": "the process is crashing and you want a layout snapshot before it disappears",
        "avoid_when": "the process is already gone, in which case only a core file helps",
        "tags": ["post-mortem", "frida", "snapshot"],
        "steps": [
            "From the attached session, enumerate modules with their base address, size and path.",
            "Snapshot thread ids and their current instruction pointers.",
            "Write the snapshot to a file outside the target's memory so it survives the crash.",
            "After the crash, compare the snapshot's module base addresses against the core or the new process.",
        ],
        "signals": ["modules-snapshotted", "threads-snapshotted", "snapshot-persisted"],
        "patterns": [
            (
                "module snapshot",
                "const mods = Process.enumerateModules().map(m => ({n: m.name, b: m.base, s: m.size, p: m.path}));\nsend({snapshot: mods, tids: Process.enumerateThreads().map(t => t.id)});\n",
            )
        ],
        "pitfalls": [
            "Storing the snapshot only in the target's memory means the crash destroys the evidence.",
            "A snapshot taken after a module was unloaded looks complete but describes the wrong layout.",
        ],
        "done_when": [
            "A module and thread snapshot is persisted outside the target.",
            "The snapshot is compared against the post-crash layout.",
        ],
        "refs": [
            "[Frida Process.enumerateModules](https://frida.re/docs/javascript-api/#process-enumeratemodules)",
        ],
        "meta": {"phase": "post-mortem"},
    },
    {
        "slug": "signal-capture",
        "title": "Capture fault signals from inside the process",
        "summary": "Install a handler that records the signal, address and backtrace before the default action terminates the process, then re-raises",
        "use_when": "the crash is not producing a usable core and you need in-process evidence",
        "avoid_when": "the process already installs its own handler that you must not displace",
        "tags": ["signal", "handler", "in-process"],
        "steps": [
            "Install a handler for SIGSEGV, SIGBUS and SIGABRT with SA_SIGINFO to receive siginfo and ucontext.",
            "In the handler, write the signal, si_addr, and a short backtrace to a pre-opened descriptor using async-signal-safe calls only.",
            "Restore the default disposition and re-raise the signal so the process still dies with the correct status.",
            "Verify the handler ran by reading the log and confirming the exit status matches the signal.",
        ],
        "signals": ["handler-installed", "signal-recorded", "status-preserved"],
        "patterns": [
            (
                "sa_siginfo handler",
                "struct sigaction sa = {0};\nsa.sa_sigaction = on_fault;\nsa.sa_flags = SA_SIGINFO | SA_RESTART;\nsigaction(SIGSEGV, &sa, NULL);\n",
            )
        ],
        "pitfalls": [
            "Calling printf or malloc in a signal handler is undefined behaviour and can deadlock the crash path.",
            "Swallowing the signal instead of re-raising changes the exit status and hides the crash from tooling.",
        ],
        "done_when": [
            "The handler records signal, address and a backtrace using safe calls only.",
            "The process still terminates with the original signal status.",
        ],
        "refs": [
            "[sigaction(2)](https://man7.org/linux/man-pages/man2/sigaction.2.html)",
            "[signal-safety(7)](https://man7.org/linux/man-pages/man7/signal-safety.7.html)",
        ],
        "meta": {"phase": "signal"},
    },
    {
        "slug": "frida-script-reload",
        "title": "Swap a Frida script without losing the session",
        "summary": "Replace a running script with an updated one in the same session so a probe fix does not cost you the attachment window",
        "use_when": "the first script has a bug or needs a new probe and the process state is expensive to recreate",
        "avoid_when": "the script installs hooks whose removal is unsafe, in which case a fresh attach is cleaner",
        "tags": ["capture", "frida", "iteration"],
        "steps": [
            "Detach every listener the old script installed and confirm no hooks remain.",
            "Load the new script into the same session and verify it evaluates without exceptions.",
            "Re-resolve probe addresses, because module load order can differ from the first script's assumptions.",
            "Record both script versions and their hashes with the capture so the evidence names what ran.",
        ],
        "signals": ["old-hooks-removed", "new-script-loaded", "versions-hashed"],
        "patterns": [
            (
                "reload",
                "session.create_script(new_source)\n# after load(): script.exports.install()\n",
            )
        ],
        "pitfalls": [
            "Reloading without detaching old listeners doubles every event and corrupts the counts.",
            "Reusing cached probe addresses across a reload can point at unmapped memory if a module was unloaded.",
        ],
        "done_when": [
            "The new script runs with no leftover hooks from the old one.",
            "Both script hashes are recorded with the capture.",
        ],
        "refs": [
            "[Frida Session API](https://frida.re/docs/javascript-api/#session)",
        ],
        "meta": {"phase": "capture"},
    },
    {
        "slug": "emitter-script-generate",
        "title": "Generate a Frida capture script from the plan",
        "summary": "Emit a runnable Frida script whose probes, argument decoding and teardown come from the instrumentation plan rather than ad-hoc editing",
        "use_when": "the plan is settled and the capture script should match it exactly",
        "avoid_when": "the target needs hand-written decoding that the emitter cannot express",
        "tags": ["capture", "emitter", "frida"],
        "steps": [
            "Read the probe list and module names from the plan, refusing to emit when a probe is unresolved.",
            "Emit one Interceptor.attach block per probe with arguments decoded by declared type.",
            "Emit the teardown block that detaches every listener and flushes the log.",
            "Hash the emitted script and store the hash beside the plan revision it came from.",
        ],
        "signals": ["script-emitted", "probes-matched-plan", "script-hashed"],
        "patterns": [
            (
                "emitter output",
                "// generated from plan rev 3\nconst P = Module.findExportByName('libparse.so', 'parse_header');\nif (P === null) throw new Error('probe unresolved: parse_header');\nInterceptor.attach(P, { onEnter(a) { send({fn: 'parse_header', n: a[1].toInt32()}); } });\n",
            )
        ],
        "pitfalls": [
            "Emitting a script with an unresolved probe and letting it throw at runtime instead of refusing at generation time.",
            "Editing the generated script by hand afterwards, which makes the hash meaningless.",
        ],
        "done_when": [
            "The emitted script matches the plan's probe list exactly.",
            "Generation refuses when a probe cannot be resolved.",
        ],
        "refs": [
            "[Frida scripting](https://frida.re/docs/quickstart/)",
        ],
        "meta": {"phase": "capture"},
    },
    {
        "slug": "emitter-gdb-macro",
        "title": "Generate a GDB command file from the plan",
        "summary": "Emit a GDB batch file that sets the planned breakpoints, captures the planned state and detaches, so a capture is one reproducible command",
        "use_when": "the capture must be reproducible by a reviewer with the same binary",
        "avoid_when": "the session needs interactive judgement at each stop",
        "tags": ["capture", "emitter", "gdb"],
        "steps": [
            "Emit set pagination off and set confirm off so the batch file cannot block on a prompt.",
            "Emit one break per planned probe and a commands block that captures the declared state and continues.",
            "Emit a final detach so the run leaves the process alive, not killed.",
            "Record the GDB version with the emitted file, because command syntax varies between releases.",
        ],
        "signals": ["batch-file-emitted", "state-capture-encoded", "detach-emitted"],
        "patterns": [
            (
                "gdb batch",
                "set pagination off\nset confirm off\nbreak parse_header\ncommands\n  silent\n  printf \"len=%d\\n\", $rsi\n  continue\nend\nrun\ndetach\n",
            )
        ],
        "pitfalls": [
            "Omitting set confirm off makes the batch file stop on a confirmation prompt and hang.",
            "A commands block that does not continue stops at the first hit and captures nothing further.",
        ],
        "done_when": [
            "The batch file runs to completion without prompting.",
            "The emitted file is stored with the capture it produced.",
        ],
        "refs": [
            "[GDB command files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Command-Files.html)",
        ],
        "meta": {"phase": "capture"},
    },
    {
        "slug": "emitter-ldpreload-capture",
        "title": "Generate an LD_PRELOAD capture library from the plan",
        "summary": "Emit C source for an interposer that logs the planned calls and forwards to the real symbols, with a build command that is part of the output",
        "use_when": "the capture must run without an external debugger attached",
        "avoid_when": "the target is statically linked or setuid, where preloading has no effect",
        "tags": ["capture", "emitter", "ldpreload"],
        "steps": [
            "Emit one wrapper per planned function with the correct declared signature.",
            "Emit dlsym RTLD_NEXT resolution guarded by a static pointer and a recursion flag.",
            "Emit the gcc command line that builds the library with -shared -fPIC and the required libraries.",
            "Compile the emitted source as part of the build step, so a non-compiling emitter fails loudly.",
        ],
        "signals": ["source-emitted", "compile-succeeds", "forwards-correctly"],
        "patterns": [
            (
                "emitter build",
                "dyninst emit ldpreload --plan plan.yml --out capture.c\ngcc -shared -fPIC -o capture.so capture.c -ldl\n",
            )
        ],
        "pitfalls": [
            "Emitting a wrapper with the wrong signature silently breaks the calling convention for that function.",
            "Shipping an emitter that was never compiled; compile the output in the build step instead of trusting the template.",
        ],
        "done_when": [
            "The emitted C compiles without warnings that affect behaviour.",
            "The resulting library forwards calls and logs them.",
        ],
        "refs": [
            "[dlsym(3)](https://man7.org/linux/man-pages/man3/dlsym.3.html)",
        ],
        "meta": {"phase": "capture"},
    },
]