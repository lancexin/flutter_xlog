// Tencent is pleased to support the open source community by making Mars available.
// Copyright (C) 2016 THL A29 Limited, a Tencent company. All rights reserved.

// Licensed under the MIT License (the "License"); you may not use this file except in
// compliance with the License. You may obtain a copy of the License at
// http://opensource.org/licenses/MIT

// Unless required by applicable law or agreed to in writing, software distributed under the License is
// distributed on an "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
// either express or implied. See the License for the specific language governing permissions and
// limitations under the License.

#include <jni.h>

#include "comm/jni/util/var_cache.h"

extern "C" jint JNI_OnLoad(JavaVM* vm, void* /*reserved*/) {
    VarCache::Singleton()->SetJvm(vm);
    return JNI_VERSION_1_6;
}

extern "C" void JNI_OnUnload(JavaVM* /*vm*/, void* /*reserved*/) {
    VarCache::Release();
}
