use serde_json::Value;
use std::io::Write;
use std::process::{Command, Stdio};

pub const FORGE_PROTOCOL_VERSION: &str = "1.0";

pub fn build_python_command(program: &str) -> Command {
    let mut command = Command::new(program);
    command.args(["-m", "kmj_forge.desktop_bridge"]);
    command
}

fn bridge_transport_error(message: &str, stderr: &[u8]) -> String {
    let stderr = String::from_utf8_lossy(stderr);
    let stderr = stderr.trim();
    if stderr.is_empty() {
        return message.to_string();
    }
    let preview: String = stderr.chars().take(1000).collect();
    format!("{message}: {preview}")
}

pub fn execute_forge_request(program: &str, request: &Value) -> Result<Value, String> {
    let request_bytes = serde_json::to_vec(request)
        .map_err(|error| format!("failed to encode Forge bridge request: {error}"))?;

    let mut command = build_python_command(program);
    command
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let mut child = command
        .spawn()
        .map_err(|error| format!("failed to start Forge Python bridge: {error}"))?;

    {
        let mut stdin = child
            .stdin
            .take()
            .ok_or_else(|| "Forge Python bridge stdin was unavailable".to_string())?;
        stdin
            .write_all(&request_bytes)
            .map_err(|error| format!("failed to write Forge bridge request: {error}"))?;
    }

    let output = child
        .wait_with_output()
        .map_err(|error| format!("failed to wait for Forge Python bridge: {error}"))?;

    let response: Value = serde_json::from_slice(&output.stdout).map_err(|error| {
        bridge_transport_error(
            &format!("Forge Python bridge returned invalid JSON ({error})"),
            &output.stderr,
        )
    })?;

    let response_version = response
        .get("protocol_version")
        .and_then(Value::as_str)
        .ok_or_else(|| "Forge Python bridge response is missing protocol_version".to_string())?;

    if response_version != FORGE_PROTOCOL_VERSION {
        return Err(format!(
            "Forge protocol mismatch: expected {FORGE_PROTOCOL_VERSION}, received {response_version}"
        ));
    }

    // The Python bridge intentionally uses non-zero exit codes for structured
    // operation failures. Preserve any valid, versioned JSON response so the
    // TypeScript bridge can surface its `ok`/`error` fields without losing context.
    Ok(response)
}

#[cfg(windows)]
fn default_python_program() -> &'static str {
    "python"
}

#[cfg(not(windows))]
fn default_python_program() -> &'static str {
    "python3"
}

#[tauri::command]
async fn forge_request(request: Value) -> Result<Value, String> {
    let program = std::env::var("KMJ_FORGE_PYTHON")
        .unwrap_or_else(|_| default_python_program().to_string());

    tauri::async_runtime::spawn_blocking(move || execute_forge_request(&program, &request))
        .await
        .map_err(|error| format!("Forge bridge task failed: {error}"))?
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![forge_request])
        .run(tauri::generate_context!())
        .expect("error while running KMJ Forge desktop");
}
