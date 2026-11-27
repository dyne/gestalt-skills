# xtd.core in application code

## Text, data and CLI boundaries

On the development revision, `xtd::string` is `xtd::basic_string<char>` containing UTF-8 code units. Its `length()` counts bytes for this specialization. For example, the UTF-8 encoding of U+00E9 occupies two units. Preserve that distinction for cursor positions, truncation and UI labels. `.chars()` gives a reference to the underlying standard string. Copy it if the receiving code needs ownership beyond the xtd string's lifetime. Use the project's ordinary STL types in its existing interfaces. Build changing text with `xtd::text::string_builder` where repeated immutable operations would copy the accumulated string.

Use `xtd::console::write_line("Read {} rows", count)` for formatted output, `xtd::console::error` for diagnostics, and the normal process exit code for failure. Keep terminal-only features such as `read_key`, cursor movement and colors out of a path that must work through pipes. Choose `xtd::parse<T>` and the appropriate `globalization::number_styles` for typed input. Check the overload and culture provider when parsing machine-readable data. Currency and date examples intentionally use a particular culture.

Use `xtd::io::file::read_all_text` or `read_all_lines` for a bounded file. For a large file, `file::open_text` returns a scoped `stream_reader`. An empty line is valid input. This complete `main.cpp` counts nonempty lines, preserves whitespace-only lines in the count and reports open errors on stderr.

```cpp
#include <xtd/console>
#include <xtd/io/file>
#include <exception>

int main(int argc, char** argv) {
  if (argc != 2) {
    xtd::console::error << "Usage: line_count FILE\n";
    return 2;
  }
  try {
    auto input = xtd::io::file::open_text(argv[1]);
    std::size_t count = 0;
    while (!input.end_of_stream()) {
      if (!input.read_line().empty()) ++count;
    }
    xtd::console::write_line("{}", count);
    return 0;
  } catch (const std::exception& error) {
    xtd::console::error << error.what() << '\n';
    return 1;
  }
}
```

For path construction use `xtd::io::path::combine`. Look at `io/file_info_open_text` for streaming and `io/binary_reader` for binary records. When wrapping a caller-owned standard stream, keep it alive while the xtd reader or writer uses it.

## Collections and queries

Use `xtd::array<T>` for fixed-size sequences, `xtd::collections::generic::list<T>` for a growable sequence, and `dictionary<K,V>` in that namespace for keyed lookup. Check the collection's failure contract before selecting indexing, adding, or a try-style lookup. A conversion to a standard container may copy elements. The `collections_generic/generic_list_conversions_to_vector` example distinguishes copying elements from explicitly moving the underlying storage.

For a query over an existing STL range, the static LINQ functions take iterable sources. For example, with `<xtd/linq/enumerable>` and `<vector>`:

```cpp
std::vector<int> samples{3, -1, 0, 8};
auto positive = [] (int value) { return value > 0; };
auto selected = xtd::linq::enumerable::where(samples, positive);
int total = 0;
for (int value : selected) total += value;  // 11
```

Here `where` is a coroutine that refers to its source and predicate during iteration. Keep both alive, including any state captured by the predicate. Materialize a result while those objects are live when returning data or keeping it for another pass. Check individual operators before assuming they own inputs or can be iterated twice. The `linq` examples cover projection, grouping, aggregation and ordering. `ranges/ranges_views_where` shows the pipe syntax for projects using xtd views.

## Choose an operating-system service

Paths in this table are under `examples/xtd.core.examples/` in the reviewed checkout. Each leads to source and its consumer target.

| Need | Entry point and decision |
| --- | --- |
| Timing and dates | Use `diagnostics::stopwatch` for elapsed work and `date_time` with `time_span` for timestamp arithmetic. Choose local or UTC at the input boundary. See `diagnostics/stopwatch`, `date_time`, `time_span` and `globalization`. |
| Logs, environment and processes | `diagnostics/console_trace_listener` and `diagnostics/debug_assert` show listeners and debug checks. Use `processes/process_with_standard_output_redirection` for a child process, inspect its exit status, and drain redirected streams as required. Environment queries and special folders are under `environment`. |
| Background work | `xtd::threading::tasks::task<T>::run(...)` schedules work, `.result()` consumes a result, and `task<>::wait_all(...)` joins a group. See `tasks/task`, `tasks/task_completion_source` and `threading/mixing_std_and_xtd_threads`. Own captured state through completion and handle failure on the observing thread. On a form, deliver results through UI dispatch. |
| Coordination and notifications | Look in `threading` for wait handles, mutexes, semaphores and joinable threads, `collections_concurrent` for queue and dictionary operations, and `delegates/event` for publisher/subscriber callbacks. For periodic work, distinguish worker timers from the event-loop timer in xtd.forms. |
| Network I/O | `net::dns` and `net::ip_address` handle host lookup and addresses. For stream protocols start with `net::sockets::tcp_client`, `tcp_listener` and `get_stream()`; for datagrams use the UDP examples. `network/tcp_client_ip_v4` demonstrates loopback binary records. Define message framing, observe end-of-stream and test with explicit listener readiness and a bounded wait. Verify the operation on the target OS. |
| IDs, numeric conversions and system failures | The `guid`, `convert`, `bit_converter`, `format` and `exceptions` groups show parsing and formatting, byte representations and typed failures. Specify byte order for persisted or network data. Catch the concrete exception when recovery depends on why an operation failed. |

For a member that resembles a .NET method, check its C++ spelling, result and implementation in the checkout. For example, the core status table lists `file` and `directory` as Complete but `file_system_watcher` as Not started. The [core examples](https://github.com/gammasoft71/xtd/tree/3ea373359f7a92885d8abd88d397fc23fa1cad7e/examples/xtd.core.examples) give working contexts to investigate where a table entry is missing or stale.
