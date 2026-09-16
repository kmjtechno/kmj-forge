use kmj_forge_desktop_lib::{build_python_command, execute_forge_request, FORGE_PROTOCOL_VERSION};
use serde_json::json;

#[test]
fn python_bridge_command_uses_direct_argv_and_versioned_protocol() {
    let command = build_python_command("python-custom");
    assert_eq!(command.get_program().to_string_lossy(), "python-custom");
    let args: Vec<_> = command.get_args().map(|arg| arg.to_string_lossy().into_owned()).collect();
    assert_eq!(args, vec!["-m", "kmj_forge.desktop_bridge"]);
    assert_eq!(FORGE_PROTOCOL_VERSION, "1.0");
}

#[test]
fn python_bridge_executes_versioned_health_round_trip() {
    let request = json!({
        "protocol_version": FORGE_PROTOCOL_VERSION,
        "operation": "health",
        "payload": {}
    });

    let response = execute_forge_request("python", &request).expect("health bridge request should succeed");
    assert_eq!(response["protocol_version"], FORGE_PROTOCOL_VERSION);
    assert_eq!(response["ok"], true);
    assert_eq!(response["result"]["protocol_version"], FORGE_PROTOCOL_VERSION);
}
