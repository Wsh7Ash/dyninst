"""Part 3 of the dyninst corpus: inspect, teardown, benchmark, scope, attach, intercept."""

from __future__ import annotations

from typing import Any

SKILLS: list[dict[str, Any]] = [
    {
        "slug": "type-inspect-module",
        "title": "Inspect a module's type environment",
        "summary": "Read the runtime type information for a module so hook signatures and struct layouts come from the target rather than from a header you assumed",
        "use_when": "you are about to decode arguments and need the real runtime layout",
        "avoid_when": "the binary is fully stripped and carries no debug or BTF type information",
        "tags": ["inspect", "types", "layout"],
        "steps": [
            "Locate the module base address and its path with Module.findBaseAddress and Module.load.",
            "Enumerate the exported symbols and record the ones matching your probe set.",
            "For struct-shaped arguments, resolve field offsets from the runtime table instead of hardcoding them.",
            "Store the resolved offsets next to the capture so a reviewer can check the decoding.",
        ],
        "signals": ["module-base-found", "symbols-enumerated", "offsets-recorded"],
        "patterns": [
            (
                "module inspect",
                "const m = Process.getModuleByName('libparse.so');\nsend({base: m.base, size: m.size, path: m.path});\nsend({exports: m.enumerateExports().filter(e => e.type === 'function').map(e => e.name)});\n",
            )
        ],
        "pitfalls": [
            "Hardcoding struct offsets from a source header that does not match the shipped build.",
            "Assuming ABI-stable layout across compiler versions and optimisation levels.",
        ],
        "done_when": [
            "The module base, path and relevant exports are recorded.",
            "Every decoded field offset is traceable to a runtime observation.",
        ],
        "refs": [
            "[Frida Module API](https://frida.re/docs/javascript-api/#module)",
        ],
        "meta": {"phase": "inspect"},
    },
    {
        "slug": "frida-enumerate-modules",
        "title": "Enumerate loaded modules to confirm what is mapped",
        "summary": "List every module with base, size and path so a probe cannot silently attach to a different copy of a library than the one you audited",
        "use_when": "several copies of a library could be loaded, for example system and bundled versions",
        "avoid_when": "the process maps more than a few thousand modules and a full dump would be noise",
        "tags": ["inspect", "modules", "mapping"],
        "steps": [
            "Call Process.enumerateModules and write the list to a file outside the process.",
            "Sort by base address and check for duplicate names with different paths.",
            "Confirm the module your probes target by path and base address, not by name alone.",
            "Compare this list against /proc/PID/maps for the same moment as a cross-check.",
        ],
        "signals": ["modules-listed", "duplicates-checked", "maps-cross-checked"],
        "patterns": [
            (
                "enumerate",
                "Process.enumerateModules().forEach(m => send([m.base.toString(), m.size, m.path]));\n",
            )
        ],
        "pitfalls": [
            "Resolving a probe by name when two modules share the name, which picks an arbitrary copy.",
            "Comparing a module list from one moment against maps from another after modules were loaded or unloaded.",
        ],
        "done_when": [
            "The module list is captured with base, size and path.",
            "The target module is identified by path and base, not name.",
        ],
        "refs": [
            "[Frida Process.enumerateModules](https://frida.re/docs/javascript-api/#process-enumeratemodules)",
        ],
        "meta": {"phase": "inspect"},
    },
    {
        "slug": "frida-types-from-module",
        "title": "Resolve a function's type from the runtime",
        "summary": "Ask Frida for a function's declared prototype so argument reading uses the real signature and varargs are handled deliberately",
        "use_when": "the function takes structs or varargs and guessing types would produce garbage",
        "avoid_when": "no type information is present and all decoding must be done from disassembly",
        "tags": ["inspect", "types", "signature"],
        "steps": [
            "Use Module.getExportByName plus DebugSymbol.getFunctionByName to reach the typed symbol.",
            "Read the prototype and record argument types and the return type verbatim.",
            "For varargs, record how many variadic arguments you actually read and why.",
            "Fall back to manual decoding only with the disassembly stored alongside as justification.",
        ],
        "signals": ["prototype-resolved", "types-recorded", "fallback-justified"],
        "patterns": [
            (
                "typed symbol",
                "const f = DebugSymbol.getFunctionByName('parse_header');\nsend({name: f.name, addr: f.address});\n",
            )
        ],
        "pitfalls": [
            "Reading a vararg that was not passed for this call shape produces a plausible but wrong value.",
            "DebugSymbol lookups fail on stripped binaries; record the failure rather than silently switching to guesses.",
        ],
        "done_when": [
            "The prototype is recorded from the runtime or its absence is documented.",
            "Vararg reads are enumerated and justified.",
        ],
        "refs": [
            "[Frida DebugSymbol](https://frida.re/docs/javascript-api/#debugsymbol)",
        ],
        "meta": {"phase": "inspect"},
    },
    {
        "slug": "memory-region-map",
        "title": "Map memory regions to classify an access",
        "summary": "Enumerate readable, writable and executable ranges so a fault or a read can be attributed to a specific mapping such as heap, stack or module",
        "use_when": "you need to explain why an address was valid, invalid or unexpectedly writable",
        "avoid_when": "the region set is changing so fast that any snapshot is stale before it is written",
        "tags": ["inspect", "memory", "mapping"],
        "steps": [
            "Enumerate ranges with Process.enumerateRanges and record base, size and protection per range.",
            "Classify the address under test by looking up the range that contains it.",
            "Compare the protection against the access type, since a write to a read-only range is a different bug from an unmapped read.",
            "Snapshot with the timestamp and note that later allocations are not represented.",
        ],
        "signals": ["ranges-enumerated", "address-classified", "snapshot-timestamped"],
        "patterns": [
            (
                "range lookup",
                "const r = Process.findRangeByAddress(ptr('0x7f0000123000'));\nsend(r ? {base: r.base, size: r.size, prot: r.protection} : {unmapped: true});\n",
            )
        ],
        "pitfalls": [
            "Treating a region snapshot as current after the program has mapped or unmapped memory.",
            "Confusing an unmapped read with a permission violation; si_code distinguishes them and the range must too.",
        ],
        "done_when": [
            "The address is classified against a timestamped range snapshot.",
            "The protection is compared with the access type.",
        ],
        "refs": [
            "[Frida Process.enumerateRanges](https://frida.re/docs/javascript-api/#process-enumerateranges)",
        ],
        "meta": {"phase": "inspect"},
    },
    {
        "slug": "teardown-verify",
        "title": "Verify the target is clean after instrumentation",
        "summary": "Confirm that every hook, breakpoint and preloaded library is removed and that the process behaves as it did before the session",
        "use_when": "the session is ending and the target must keep running normally",
        "avoid_when": "the process is being deliberately terminated as part of the test",
        "tags": ["teardown", "verify", "cleanup"],
        "steps": [
            "Detach every listener and confirm the count of active hooks is zero.",
            "Compare the module list against the pre-session snapshot to prove no injected library remains.",
            "Re-run the baseline input and compare the result with the stored baseline.",
            "Record the teardown evidence, including any difference that could not be removed.",
        ],
        "signals": ["hooks-zero", "modules-match-baseline", "behaviour-matches"],
        "patterns": [
            (
                "teardown check",
                "session.detach()\n# then compare Process.enumerateModules() with the pre-session snapshot\n",
            )
        ],
        "pitfalls": [
            "Assuming detach removed a hook that was installed by a preloaded library; preload survives until process exit.",
            "Declaring the target clean without re-running the baseline, which is the only behavioural proof.",
        ],
        "done_when": [
            "Hook count is zero and the module list matches the pre-session snapshot.",
            "The baseline input produces the baseline result again.",
        ],
        "refs": [
            "[Frida Session.detach](https://frida.re/docs/javascript-api/#session-detach)",
        ],
        "meta": {"phase": "teardown"},
    },
    {
        "slug": "teardown-force-detach",
        "title": "Recover a wedged session without killing the target",
        "summary": "Detach from a process whose script has hung or whose hook recursed, using the least destructive step that restores normal execution",
        "use_when": "the target is unresponsive because instrumentation is stuck",
        "avoid_when": "the process is already dead, where recovery is pointless",
        "tags": ["teardown", "recovery", "hung"],
        "steps": [
            "Check whether the target is stopped in the debugger or spinning in a hook before choosing a recovery step.",
            "For a GDB stop, issue detach which resumes the process; for a Frida hang, kill only the agent session.",
            "If the hook recursed, unload the script rather than detaching the whole session so other probes survive.",
            "Confirm recovery by observing a normal request complete, then record what was recovered and what was lost.",
        ],
        "signals": ["state-diagnosed", "least-destructive-recovery", "recovery-confirmed"],
        "patterns": [
            (
                "recover gdb stop",
                "gdb -p 4711 -batch -ex 'detach'\n# or from an existing session: detach\n",
            )
        ],
        "pitfalls": [
            "Killing the process to recover from a hung hook destroys the bug site and any unsaved evidence.",
            "Detaching without diagnosing leaves the root cause in place for the next run.",
        ],
        "done_when": [
            "The target is running normally again and the recovery step is recorded.",
            "Evidence lost by the recovery is stated explicitly.",
        ],
        "refs": [
            "[GDB detach](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Attach.html)",
        ],
        "meta": {"phase": "teardown"},
    },
    {
        "slug": "signal-handler-safe-unload",
        "title": "Remove a hook without racing its own signal handler",
        "summary": "Order the teardown so a fault signal cannot arrive while the hook is being removed, which would otherwise crash the process during cleanup",
        "use_when": "the instrumentation installs a signal handler and also hooks code that can fault",
        "avoid_when": "no signal handler is involved and a plain detach is enough",
        "tags": ["teardown", "signal", "race"],
        "steps": [
            "Block the relevant signals on all threads before beginning removal, using pthread_sigmask.",
            "Remove the hooks, then restore the original handler, then unblock the signals.",
            "Check that no signal was delivered while blocked by reading the pending set before unblocking.",
            "Record the ordering used, because the reverse order reintroduces the race.",
        ],
        "signals": ["signals-blocked", "teardown-ordered", "pending-checked"],
        "patterns": [
            (
                "block then teardown",
                "sigset_t s; sigemptyset(&s); sigaddset(&s, SIGSEGV);\npthread_sigmask(SIG_BLOCK, &s, NULL);\n/* remove hooks, restore handler */\npthread_sigmask(SIG_UNBLOCK, &s, NULL);\n",
            )
        ],
        "pitfalls": [
            "Restoring the handler before removing the hook, so a fault in the hook calls the default action.",
            "Blocking signals only on the calling thread while other threads keep faulting into the hook.",
        ],
        "done_when": [
            "Signals are blocked on all threads across the removal window.",
            "The ordering is recorded and the pending set was empty at unblock.",
        ],
        "refs": [
            "[pthread_sigmask(3)](https://man7.org/linux/man-pages/man3/pthread_sigmask.3.html)",
        ],
        "meta": {"phase": "teardown"},
    },
    {
        "slug": "frida-unload",
        "title": "Unload a Frida script and leave no hooks behind",
        "summary": "Detach listeners, unload the script and prove the process returns to its uninstrumented behaviour before the session closes",
        "use_when": "the capture window has closed and the same process must keep running",
        "avoid_when": "the process is being killed at the end of the test anyway",
        "tags": ["teardown", "frida", "unload"],
        "steps": [
            "Call detach on every Interceptor listener created by the script and keep the returned handles.",
            "Unload the script with session.detach or script.unload and check for an exception.",
            "Re-resolve a probe address to confirm the function now points at its original prologue.",
            "Record the unload and the verification in the session log.",
        ],
        "signals": ["listeners-detached", "script-unloaded", "prologue-restored"],
        "patterns": [
            (
                "detach listener",
                "const listener = Interceptor.attach(p, callbacks);\n// at the end\nlistener.detach();\n",
            )
        ],
        "pitfalls": [
            "Unloading the script without detaching listeners leaves trampolines in the target's code.",
            "Assuming detach restored the prologue without checking the first bytes at the address.",
        ],
        "done_when": [
            "Every listener is detached and the script is unloaded.",
            "The probe address shows the original code again.",
        ],
        "refs": [
            "[Frida Interceptor detach](https://frida.re/docs/javascript-api/#interceptor)",
        ],
        "meta": {"phase": "teardown"},
    },
    {
        "slug": "emitter-benchmark",
        "title": "Measure the cost of an emitter before trusting its captures",
        "summary": "Time the instrumented run against the baseline so overhead is a number you report rather than an assumption you make",
        "use_when": "the finding depends on timing or throughput and instrumentation could distort it",
        "avoid_when": "the capture is purely structural and timing is irrelevant to the claim",
        "tags": ["benchmark", "overhead", "timing"],
        "steps": [
            "Run the baseline and the instrumented run at least five times each with the same input.",
            "Record wall time, CPU time and event count for every run, then report median and spread.",
            "Compute the overhead ratio and state whether the claim survives that distortion.",
            "Keep the raw timings, not only the summary, so the measurement can be re-checked.",
        ],
        "signals": ["runs-repeated", "timings-recorded", "overhead-reported"],
        "patterns": [
            (
                "timing loop",
                "for i in 1 2 3 4 5; do /usr/bin/time -f '%e %U %S' ./target --input case01.bin; done\n",
            )
        ],
        "pitfalls": [
            "Comparing a single instrumented run to a single baseline run and calling the difference overhead.",
            "Reporting a speedup or slowdown without the spread, which hides that the runs overlapped.",
        ],
        "done_when": [
            "At least five runs per condition are recorded with median and spread.",
            "The overhead ratio is stated with the effect on the claim.",
        ],
        "refs": [
            "[time(1)](https://man7.org/linux/man-pages/man1/time.1.html)",
        ],
        "meta": {"phase": "benchmark"},
    },
    {
        "slug": "overhead-control-run",
        "title": "Run a no-op control to separate hook cost from probe cost",
        "summary": "Instrument with hooks that capture nothing so the cost of attachment itself is separated from the cost of the observations",
        "use_when": "overhead is high and you need to know whether the hook or the logging dominates",
        "avoid_when": "the overhead is already negligible relative to the noise floor",
        "tags": ["benchmark", "control", "overhead"],
        "steps": [
            "Build a variant of the script that attaches the same probes but records nothing.",
            "Run the no-op variant and the full-capture variant with the same input and repetition count.",
            "Compare the two against the baseline to attribute cost to attachment versus logging.",
            "Report all three timings so the attribution is visible rather than asserted.",
        ],
        "signals": ["noop-variant-built", "three-way-compared", "attribution-reported"],
        "patterns": [
            (
                "noop hook",
                "Interceptor.attach(p, { onEnter(args) { /* record nothing */ } });\n",
            )
        ],
        "pitfalls": [
            "Skipping the no-op control and blaming logging for cost that attachment already imposes.",
            "Letting the compiler optimise away the no-op path in a way that makes it not comparable.",
        ],
        "done_when": [
            "Three timings exist: baseline, no-op hook and full capture.",
            "The attribution between attachment and logging is stated with numbers.",
        ],
        "refs": [
            "[Frida performance notes](https://frida.re/docs/performance/)",
        ],
        "meta": {"phase": "benchmark"},
    },
    {
        "slug": "cross-arch-normalize",
        "title": "Normalise captures across architectures",
        "summary": "Convert register and calling-convention details into a common record shape so an x86-64 capture and an arm64 capture can be compared directly",
        "use_when": "the same bug must be evidenced on more than one architecture",
        "avoid_when": "only one architecture is in scope, where normalisation adds indirection for nothing",
        "tags": ["benchmark", "portability", "normalisation"],
        "steps": [
            "Record the architecture and ABI with every capture, including pointer width and endianness.",
            "Map argument registers to positional argument names before analysis rather than after.",
            "Convert addresses to module-relative offsets so ASLR does not make two runs look different.",
            "Keep the raw registers alongside the normalised record so the mapping can be audited.",
        ],
        "signals": ["arch-recorded", "args-positional", "offsets-relative"],
        "patterns": [
            (
                "normalise",
                "send({arch: Process.arch, ptr: Process.pointerSize, fn: 'parse_header', off: addr.sub(base), args: [a0, a1]});\n",
            )
        ],
        "pitfalls": [
            "Comparing absolute addresses across runs where ASLR changed the base and calling the difference a bug.",
            "Assuming x86-64 argument order on arm64, where the registers and vararg rules differ.",
        ],
        "done_when": [
            "Every record names its architecture and uses module-relative offsets.",
            "Raw register values are preserved beside the normalised form.",
        ],
        "refs": [
            "[Frida Process.arch](https://frida.re/docs/javascript-api/#process-arch)",
        ],
        "meta": {"phase": "benchmark"},
    },
    {
        "slug": "scope-enforce-plan",
        "title": "Refuse instrumentation outside the authorised scope",
        "summary": "Check the plan's target against a written scope document before any attach, so an out-of-scope process is never instrumented by accident",
        "use_when": "the engagement has a written scope and several targets are available on the host",
        "avoid_when": "the target is your own test binary and scope is not a concept that applies",
        "tags": ["scope", "authorisation", "guard"],
        "steps": [
            "Write the scope as a machine-readable list of host and binary identifiers before starting.",
            "Check the resolved target against that list and abort with a clear message when it does not match.",
            "Record the scope revision and the check result in the evidence bundle.",
            "Re-check after any respawn or redeploy, because the identifier can change while the name stays the same.",
        ],
        "signals": ["scope-loaded", "target-checked", "check-recorded"],
        "patterns": [
            (
                "scope check",
                "python -m dyninst scope check --plan plan.yml --scope scope.json || exit 1\n",
            )
        ],
        "pitfalls": [
            "Matching by process name alone, which can select a different binary with the same name.",
            "Checking scope once at the start and never again after a redeploy changed the build.",
        ],
        "done_when": [
            "An out-of-scope target is refused before any attach.",
            "The scope revision and check result are recorded.",
        ],
        "refs": [
            "[PTES scoping](https://www.pentest-standard.org/index.php/Scoping)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "scope-validate-imports",
        "title": "Check that instrumentation only touches in-scope modules",
        "summary": "Compare every module the plan resolves against the scope list so a probe cannot silently land in a vendor library that is out of scope",
        "use_when": "the target loads third-party or vendor libraries that the engagement excludes",
        "avoid_when": "every loaded module is in scope by definition",
        "tags": ["scope", "modules", "validation"],
        "steps": [
            "Enumerate the modules the plan will touch after resolution, not the ones you intended to touch.",
            "Compare the resolved module paths against the scope list and list every mismatch.",
            "Drop or refuse any probe that resolves into an excluded module, and record the refusal.",
            "Store the resolved-to-scope mapping with the capture so the boundary is auditable.",
        ],
        "signals": ["modules-resolved", "scope-compared", "refusals-recorded"],
        "patterns": [
            (
                "import check",
                "python -m dyninst scope imports --plan plan.yml --scope scope.json\n",
            )
        ],
        "pitfalls": [
            "Resolving by symbol name and landing in a vendor copy of the library that is excluded.",
            "Recording only the intended modules rather than the ones the symbol resolution actually selected.",
        ],
        "done_when": [
            "Every resolved module is checked against scope and mismatches are refused.",
            "The mapping is stored with the capture.",
        ],
        "refs": [
            "[PTES scoping](https://www.pentest-standard.org/index.php/Scoping)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "scope-merge-two-plans",
        "title": "Merge two instrumentation plans without widening scope",
        "summary": "Combine plans from two sessions into one and fail when the union exceeds either authorised scope, instead of silently inheriting the larger one",
        "use_when": "two teams or two sessions produced plans for the same target and they must run together",
        "avoid_when": "the plans were authorised under the same scope and a merge cannot add anything",
        "tags": ["scope", "merge", "authorisation"],
        "steps": [
            "Load both plans with their scope references and compute the union of probes and targets.",
            "Check the union against the intersection of the two scopes, since a merge cannot widen what was authorised.",
            "Fail with the specific out-of-scope entries rather than producing a merged plan that quietly exceeds scope.",
            "Record both source plan revisions and the merged revision in the result.",
        ],
        "signals": ["plans-loaded", "intersection-checked", "revision-recorded"],
        "patterns": [
            (
                "merge check",
                "python -m dyninst scope merge --a plan-a.yml --b plan-b.yml --scope-a sa.json --scope-b sb.json\n",
            )
        ],
        "pitfalls": [
            "Unioning the scopes as well as the probes, which authorises work neither engagement covered.",
            "Merging without recording the source revisions, so the merged plan cannot be traced back.",
        ],
        "done_when": [
            "The merged plan is checked against the scope intersection and refuses on excess.",
            "Source and merged revisions are recorded.",
        ],
        "refs": [
            "[PTES scoping](https://www.pentest-standard.org/index.php/Scoping)",
        ],
        "meta": {"phase": "scope"},
    },
    {
        "slug": "gdb-remote-target",
        "title": "Attach GDB to a remote target through gdbserver",
        "summary": "Debug a process on another host through gdbserver, keeping the binary and symbol files local so the capture is attributable to a known build",
        "use_when": "the target runs on a host you cannot run a debugger on directly",
        "avoid_when": "the network path to the target is not authorised or not encrypted",
        "tags": ["attach", "gdb", "remote"],
        "steps": [
            "Start gdbserver on the target host bound to a specific interface and port, and record both.",
            "Copy the exact binary and its debug symbols to the analysis host and confirm the build-id matches.",
            "Connect with target remote host:port and verify the reported architecture and thread list.",
            "Capture state, then detach so the remote process continues instead of being killed.",
        ],
        "signals": ["gdbserver-bound", "build-id-matched", "remote-detached"],
        "patterns": [
            (
                "remote attach",
                "gdbserver 127.0.0.1:2345 --attach 4711\n# locally\ngdb -q ./server -ex 'target remote 127.0.0.1:2345' -ex 'info threads' -ex 'detach'\n",
            )
        ],
        "pitfalls": [
            "Binding gdbserver to all interfaces exposes an unauthenticated debug port to the network.",
            "Debugging with symbols from a different build produces frame names that are confidently wrong.",
        ],
        "done_when": [
            "gdbserver is bound to an authorised interface and the build-id matches the local binary.",
            "The remote process continues after detach.",
        ],
        "refs": [
            "[gdbserver](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Server.html)",
        ],
        "meta": {"phase": "attach"},
    },
    {
        "slug": "ldpreload-net-intercept",
        "title": "Intercept outbound connections with a preload hook",
        "summary": "Hook connect and getaddrinfo to record every destination a process tries to reach, which is evidence a network claim needs",
        "use_when": "you need to show where a process connects, including failed attempts",
        "avoid_when": "the target issues raw syscalls or uses a statically linked resolver",
        "tags": ["intercept", "ldpreload", "network"],
        "steps": [
            "Interpose connect and getaddrinfo, resolving the originals with dlsym RTLD_NEXT.",
            "Decode the sockaddr by family: IPv4, IPv6 and unix sockets each need different handling.",
            "Record the destination and the result, including errno, so failed attempts are visible.",
            "Cross-check against a packet capture or ss output to prove the hook's coverage.",
        ],
        "signals": ["connect-hooked", "destinations-recorded", "coverage-cross-checked"],
        "patterns": [
            (
                "connect hook",
                "int connect(int fd, const struct sockaddr *addr, socklen_t len) {\n  log_sockaddr(addr, len);\n  int rc = real_connect(fd, addr, len);\n  log_result(rc, errno);\n  return rc;\n}\n",
            )
        ],
        "pitfalls": [
            "Casting every sockaddr to sockaddr_in without checking sa_family, which misreports IPv6 and unix sockets.",
            "Logging only successful connections, which hides the blocked destinations that often matter most.",
        ],
        "done_when": [
            "Every connect attempt is recorded with family-correct decoding and result.",
            "Coverage is checked against an independent observation.",
        ],
        "refs": [
            "[connect(2)](https://man7.org/linux/man-pages/man2/connect.2.html)",
            "[getaddrinfo(3)](https://man7.org/linux/man-pages/man3/getaddrinfo.3.html)",
        ],
        "meta": {"phase": "intercept"},
    },
]