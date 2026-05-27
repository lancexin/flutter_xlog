plugins {
    id("com.android.library")
}

android {
    namespace = "com.tencent.mars.xlog"
    compileSdk = 36
    ndkVersion = "27.0.12077973"
    defaultConfig {
        minSdk = 19
        // targetSdkVersion is no longer used by AGP for libraries; kept implicit.
        ndk {
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }
    sourceSets {
        getByName("main") {
            java.srcDir("src/main/java")
            // libmarsxlog.so + libc++_shared.so produced by build_android.py
            jniLibs.srcDir("../../output/android/libs")
            manifest.srcFile("src/main/AndroidManifest.xml")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_7
        targetCompatibility = JavaVersion.VERSION_1_7
    }
    buildTypes {
        getByName("release") {
            proguardFile("proguard-rules.pro")
        }
    }
}
