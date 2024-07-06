Note: Read KivyApp_to_APK.ipyb For Setup

---

# Kivy Mobile Development Setup Guide for Django Integration

## Prerequisites

- **Root User Warning**: It's recommended to use a normal user for security reasons, especially when running Django on Android.
- Ensure Python, pip, and Buildozer are installed.
- Set `android-ndk` version in `buildozer.spec` to `26b` and rename to `25b` as needed.

## Configuration

- Update service and package names in `buildozer.spec`:
  - Example:
    ```ini
    android-ndk = 26b
    service = org.kivy.android.PythonService
    package.name = org.kivy.android.PythonActivity
    ```

## Project Structure

- **Django Project**: Place your Django project files in the `service/` directory.
- **Kivy App**: Develop your Kivy app in the `tool/` directory.

## Setup Process

1. **Clone Repository**: 
   ```bash
   git clone https://github.com/SecretDiscorder/djavy.git
   ```

2. **Organize Files**: 
   Move all Django project files to the main collaboration directory.

## Screenshots

![Screenshot 1](https://github.com/SecretDiscorder/djavy/assets/139457966/d192a606-b0ba-4244-84bf-6157f881608a)

![Screenshot 2](https://github.com/SecretDiscorder/djavy/assets/139457966/c15e8f9e-db3c-4d54-a4d3-aff8b9916ffb)

![Screenshot 3](https://github.com/SecretDiscorder/djavy/assets/139457966/9e0b3cd5-07ba-4f6d-8331-0c529e6357ed)

## Build Instructions

- Build your Android APK using Buildozer on Debian 12 AMD X86_64.

   ```bash
   buildozer android debug
   ```

   Ensure your app's APK is located in `bin/myapp...apk`.

## Notes

- **Operating System**: Avoid using Collab or Windows; Ubuntu/Debian is recommended.
- **Development Environment**: This setup assumes you are using Kivy and p4a with Buildozer.

---

buildozer.spec default configuration. All Script and Kivy UI in main.py (do not change)
