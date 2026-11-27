# xtd.tunit

Create a separate test executable. Use the application's library target or share its model sources so checks exercise the implementation used by the application. With the xtd CMake helpers use `target_type(TEST_APPLICATION)` after `add_sources(...)` and any `add_references(...)`. This registers the executable with CTest. In a larger build enable testing in the top-level project for discovery from its build directory.

```cpp
#include <xtd/string>
#include <xtd/tunit/assert>
#include <xtd/tunit/console_unit_test>
#include <xtd/tunit/test_class>
#include <xtd/tunit/test_class_attribute>

namespace text_tests {
  class test_class_(utf8_text) {
    void test_method_(counts_utf8_code_units) {
      xtd::string text{u8"caf\u00e9"};
      xtd::tunit::assert::are_equal(std::size_t{5}, text.length());
    }
  };
}

int main() {
  return xtd::tunit::console_unit_test().run();
}
```

`test_class_` and `test_method_` register the suite and the case. Compile each case's translation unit into the runner; static archives can discard objects whose only effect is registration. Return `run()`'s exit status. The alternative `TUNIT_CONFIG_MAIN` goes before `<xtd/xtd.tunit>` in one translation unit and supplies the entry point.

| What the test needs | Mechanism |
| --- | --- |
| A failed precondition makes the next operation invalid | `assert::` stops the current test on failure. In equality checks pass expected, then actual. |
| Several independent diagnostics in one run | `valid::` records a failure and execution continues. Use it where later checks remain meaningful. |
| Conditional execution based on an external prerequisite | `assume::` records an aborted test on an unmet assumption. Inspect the runner summary for cases that actually executed. |
| Domain-specific comparison | Use `string_assert`, `collection_assert`, `file_assert` or `directory_assert`. The constraints examples also show `assert_that(...)`. Some examples intentionally fail to demonstrate diagnostics. |
| Fixture state | Use `test_initialize_` / `test_cleanup_` for each case and `class_initialize_` / `class_cleanup_` for suite setup/teardown. Check macro signatures in the project's SDK. Use scope-bound C++ objects for local resources. |

With a configured consumer, build the test target, then run `ctest --test-dir build -C Release --output-on-failure --no-tests=error`. For the runner itself, use `--list_tests` to see registered names and quote a filter such as `'--filter_tests=*utf8_text.counts_utf8_code_units'`. Use `--output=xml:results.xml` for structured output on the reviewed revision. CTest filters target names; the tunit filter selects cases inside the executable. Check the selected case count as well as the process status.

See [tunit examples](https://github.com/gammasoft71/xtd/tree/3ea373359f7a92885d8abd88d397fc23fa1cad7e/examples/xtd.tunit.examples), especially `hello_worlds/hello_world_tunit_without_helpers` for explicit registration and `others/create_gtest_like_event_listener` for custom reporting.
