#
# To learn more about a Podspec see http://guides.cocoapods.org/syntax/podspec.html.
# Run `pod lib lint flutter_xlog.podspec` to validate before publishing.
#
Pod::Spec.new do |s|
  s.name             = 'flutter_xlog'
  s.version          = '0.0.1'
  s.summary          = 'A plugin for using xlog (mars-xlog) in a Flutter project.'
  s.description      = <<-DESC
A plugin for using xlog (mars-xlog) in a Flutter project.
                       DESC
  s.homepage         = 'https://github.com/Tencent/mars'
  s.license          = { :file => '../LICENSE' }
  s.author           = { 'Tencent' => 'mars@tencent.com' }
  s.source           = { :path => '.' }
  s.source_files = 'Classes/**/*'
  s.vendored_libraries = 'xlog/libxlog.a'
  s.preserve_paths = 'xlog/include/**/*.h', 'xlog/libxlog.a'

  # Build libxlog.a + headers via xlog/build_ios.py and stage them under xlog/
  # before `pod install`. See ios/prepare_xlog_lib.sh for the helper.
  s.prepare_command = <<-CMD
    sh prepare_xlog_lib.sh
  CMD

  s.dependency 'Flutter'
  s.platform = :ios, '13.0'
  s.static_framework = false
  s.libraries = 'z', 'c++'

  # Flutter.framework does not contain a i386 slice.
  s.pod_target_xcconfig = {
    'DEFINES_MODULE' => 'YES',
    'EXCLUDED_ARCHS[sdk=iphonesimulator*]' => 'i386',
    'HEADER_SEARCH_PATHS' => '"${PODS_TARGET_SRCROOT}/xlog/include"',
  }
  s.swift_version = '5.0'
end
