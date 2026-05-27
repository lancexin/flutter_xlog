import com.android.build.gradle.LibraryExtension
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

group = "com.tencent.xlog"
version = "1.0-SNAPSHOT"

buildscript {
    val kotlinVersion = "1.9.24"
    repositories {
        google()
        mavenCentral()
    }

    dependencies {
        classpath("com.android.tools.build:gradle:8.7.2")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlinVersion")
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

apply(plugin = "com.android.library")
apply(plugin = "kotlin-android")

extensions.configure<LibraryExtension>("android") {
    compileSdk = 36
    ndkVersion = "27.0.12077973"
    namespace = "com.tencent.xlog.flutter"

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    sourceSets.getByName("main") {
        java.srcDir("src/main/kotlin")
        // Reuse the standalone Android module's Java sources (Xlog.java, Log.java).
        java.srcDir("../../platform/android/src/main/java")
        // Pre-built libmarsxlog.so + libc++_shared.so staged by
        // prepare_xlog_libs.sh — avoids re-running CMake on every build.
        jniLibs.srcDir("src/main/jniLibs")
    }

    defaultConfig {
        minSdk = 21
        ndk {
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }
}

// Run prepare_xlog_libs.sh before the native-lib merge so the .so files exist
// the first time someone builds the plugin (or after `flutter clean`).
val prepareXlogLibs = tasks.register<Exec>("prepareXlogLibs") {
    val script = file("prepare_xlog_libs.sh")
    val jniLibs = file("src/main/jniLibs")
    inputs.file(script)
    outputs.dir(jniLibs)
    workingDir = projectDir
    val androidExt = extensions.getByType(LibraryExtension::class.java)
    doFirst {
        environment("NDK_ROOT", androidExt.ndkDirectory.absolutePath)
    }
    commandLine("bash", script.absolutePath)
}

afterEvaluate {
    tasks.matching { it.name.startsWith("merge") && it.name.endsWith("JniLibFolders") }
        .configureEach { dependsOn(prepareXlogLibs) }
    tasks.matching { it.name.startsWith("merge") && it.name.endsWith("NativeLibs") }
        .configureEach { dependsOn(prepareXlogLibs) }
}

tasks.withType<KotlinCompile>().configureEach {
    kotlinOptions {
        jvmTarget = "1.8"
    }
}
