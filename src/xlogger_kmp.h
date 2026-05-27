
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

void Kmp_initLogFile(
        int level, int appendMode,
        const char* cacheDir, const char* logDir,
        const char* namePrefix, const char* pubKey
);

void Kmp_setMaxAliveTime(long maxAliveTime);

void Kmp_setConsoleLogOpen(bool open);

void Kmp_writeLog(int level, const char* tag, int pid, int tid, int main_tid, const char* msg);

void Kmp_flush(bool sync);

#ifdef __cplusplus
}
#endif