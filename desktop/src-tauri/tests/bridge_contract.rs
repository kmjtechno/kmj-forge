use kmj_forge_desktop_lib::{build_python_command, FORGE_PROTOCOL_VERSION};

#[test]
fn python_bridge_command_uses_direct_argv_and_versioned_protocol() {
    let command = build_python_command("python-custom");
    assert_eq!(command.get_program().to_string_lossy(), "python-custom");
    let args: Vec<_> = command.get_args().map(|arg| arg.to_string_lossy().into_owned()).collect();
    assert_eq!(args, vec!["-m", "kmj_forge.desktop_bridge"]);
    assert_eq!(FORGE_PROTOCOL_VERSION, "1.0");
}
