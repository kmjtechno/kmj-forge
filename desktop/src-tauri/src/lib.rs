use std::process::Command;

pub const FORGE_PROTOCOL_VERSION: &str = "1.0";

pub fn build_python_command(program: &str) -> Command {
    let mut command = Command::new(program);
    command.args(["-m", "kmj_forge.desktop_bridge"]);
    command
}

pub fn run() {
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running KMJ Forge desktop");
}
