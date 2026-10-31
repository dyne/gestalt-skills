# GNU Make

## Preserve the dependency graph

- Respect supplied `CC`, `CXX`, `CPPFLAGS`, `CFLAGS`, `CXXFLAGS`, `LDFLAGS` and
  `LDLIBS`. Keep preprocessor flags in compilation and libraries after objects
  on the link line. Link C++ objects with the C++ driver unless the project
  deliberately supplies its runtime another way.
- Give each source a unique object path. Separate incompatible configurations;
  Make does not normally detect a changed command or changed compiler flags.
  Use explicit configuration dependencies or a fresh variant directory.
- Set the intended default goal before included dependency files. Mark action
  targets such as `all`, `test` and `clean` as `.PHONY`; real outputs must not
  be phony. Use order-only directory prerequisites to avoid rebuilds caused
  solely by directory timestamps. Recipes normally require literal tabs.

For GCC/Clang-style compilers, this pattern preserves nested paths and tracks
headers; adapt the existing graph rather than replacing the whole Makefile:

```makefile
.DEFAULT_GOAL := all
CCACHE ?= $(shell command -v ccache 2>/dev/null)
SOURCES := src/main.c src/util.c
OBJECTS := $(patsubst %.c,build/%.o,$(SOURCES))
DEPFILES := $(OBJECTS:.o=.d)
.PHONY: all
all: build/app

build/app: $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $(OBJECTS) $(LDLIBS)

build/%.o: %.c
	@mkdir -p $(@D)
	$(CCACHE) $(CC) $(CPPFLAGS) $(CFLAGS) -MMD -MP -MF $(@:.o=.d) -MT $@ -c $< -o $@

-include $(DEPFILES)
```

The compile-only `CCACHE` prefix automatically enables a detected cache and is
empty when it is absent. With this hook, `make CCACHE=ccache` explicitly enables
it and `make CCACHE=` disables it; use the project's equivalent launcher
variable when one exists. GNU Make has no universal ccache flag. Keep `CC`/`CXX`
and the link recipe unchanged, and avoid adding the prefix if the compiler is
already wrapped. Check verbose recipe output to verify cache use.

Declare generated headers as explicit prerequisites for the first build;
included `.d` files cannot supply a dependency that has not yet been recorded.
For C++, adapt the source suffix, compiler and language flags together. Use
`$@` for the target, `$<` for the first prerequisite and `$^` only when every
prerequisite belongs on the command line and deduplication is acceptable.

## Diagnose incremental and parallel failures

Inspect rules, timestamps and the actual failed command before forcing a
rebuild. `make --trace <target>` explains rebuild decisions. `make -n` prints
recipes but is not a security sandbox: expansion and recursive-make behavior
can still execute commands. `V=1` works only when the Makefile implements it.
"Nothing to be done" can be a correct result; do not touch files just to hide it.

Verify a clean build, an unchanged no-op build and a header edit that rebuilds
the expected consumers. Exercise a bounded parallel build for graph changes;
fix missing edges rather than hiding races by disabling parallelism. Use
`$(MAKE)` for recursive invocations to preserve flags and the jobserver. Clean
only known outputs, and honor `PREFIX`/`DESTDIR` when installation is in scope.

Source: [GNU Make manual](https://www.gnu.org/software/make/manual/make.html).
