use cpython::{PyResult, Python, py_module_initializer, py_fn};
use harsh::HarshBuilder;

py_module_initializer!(myrust_shortener, |py, m| {
    m.add(py, "__doc__", "This module is implemented in Rust.")?;
    m.add(py, "shorten", py_fn!(py, shorten_py(a: u64)))?;
    Ok(())
});

fn shorten(counter: u64) -> String {
    let harsh = HarshBuilder::new().init().unwrap();
    harsh.encode(&[counter]).unwrap()
}

fn shorten_py(_: Python, a:u64) -> PyResult<String> {
    let out = shorten(a);
    Ok(out)
}
