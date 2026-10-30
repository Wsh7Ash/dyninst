dyninst Skill Catalog

50 skills across 13 phases.

| `slug` | title | phase |
|---|---|---|
| `core-dump-analyze` | Analyse a core dump for the crashing instruction | post-mortem |
| `crash-signal-decode` | Decode the crash signal and faulting address | post-mortem |
| `cross-arch-normalize` | Normalise captures across architectures | benchmark |
| `ebpf-kprobe` | Attach an eBPF kprobe to a kernel function | kernel |
| `ebpf-tracepoint` | Use a stable tracepoint instead of a raw kprobe | kernel |
| `ebpf-uprobe` | Attach an eBPF uprobe to a user-space function | kernel |
| `emitter-benchmark` | Measure the cost of an emitter before trusting its captures | benchmark |
| `emitter-gdb-macro` | Generate a GDB command file from the plan | capture |
| `emitter-ldpreload-capture` | Generate an LD_PRELOAD capture library from the plan | capture |
| `emitter-script-generate` | Generate a Frida capture script from the plan | capture |
| `frida-attach` | Attach Frida to an already running process | attach |
| `frida-enumerate-modules` | Enumerate loaded modules to confirm what is mapped | inspect |
| `frida-hook-native` | Replace a native function with Frida Interceptor | intercept |
| `frida-java-hook` | Hook a Java method with Frida on Android | intercept |
| `frida-post-mortem-core` | Capture a Frida snapshot before the process is torn down | post-mortem |
| `frida-script-reload` | Swap a Frida script without losing the session | capture |
| `frida-spawn` | Spawn the target under Frida from the first instruction | attach |
| `frida-stalker-trace` | Trace executed code with Frida Stalker | trace |
| `frida-types-from-module` | Resolve a function's type from the runtime | inspect |
| `frida-unload` | Unload a Frida script and leave no hooks behind | teardown |
| `gdb-attach` | Attach GDB to a running process and stop it safely | attach |
| `gdb-break-condition` | Break only on the call you care about | debug |
| `gdb-breakpoint` | Stop execution at a function with a GDB breakpoint | debug |
| `gdb-frame-capture` | Capture a backtrace that survives review | post-mortem |
| `gdb-remote-target` | Attach GDB to a remote target through gdbserver | attach |
| `gdb-stepi` | Single-step instructions to follow a branch precisely | debug |
| `gdb-tracepoints` | Collect data with GDB tracepoints instead of stopping | trace |
| `gdb-watchpoint` | Catch a write to memory with a GDB watchpoint | debug |
| `ldpreload-constructor` | Run setup code before main with a constructor | intercept |
| `ldpreload-hook` | Interpose a libc function with an LD_PRELOAD hook | intercept |
| `ldpreload-launch` | Launch a target with an LD_PRELOAD interposer | attach |
| `ldpreload-net-intercept` | Intercept outbound connections with a preload hook | intercept |
| `ldpreload-syscall` | Intercept a syscall wrapper rather than raw system calls | intercept |
| `memory-region-map` | Map memory regions to classify an access | inspect |
| `overhead-control-run` | Run a no-op control to separate hook cost from probe cost | benchmark |
| `plan-baseline-capture` | Capture a clean baseline before instrumenting | plan |
| `plan-emitter-select` | Choose the emitter that fits the target constraints | plan |
| `plan-generate` | Write an instrumentation plan before touching the target | plan |
| `plan-probe-map` | Map probe points to real symbols before attaching | plan |
| `probe-function-entry` | Observe function entry with typed arguments | trace |
| `probe-function-return` | Observe function return and error paths | trace |
| `probe-multi-entry` | Trace several functions as one ordered timeline | trace |
| `scope-enforce-plan` | Refuse instrumentation outside the authorised scope | scope |
| `scope-merge-two-plans` | Merge two instrumentation plans without widening scope | scope |
| `scope-validate-imports` | Check that instrumentation only touches in-scope modules | scope |
| `signal-capture` | Capture fault signals from inside the process | signal |
| `signal-handler-safe-unload` | Remove a hook without racing its own signal handler | teardown |
| `teardown-force-detach` | Recover a wedged session without killing the target | teardown |
| `teardown-verify` | Verify the target is clean after instrumentation | teardown |
| `type-inspect-module` | Inspect a module's type environment | inspect |
