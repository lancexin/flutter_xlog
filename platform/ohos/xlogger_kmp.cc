
#include "xlog/xlogger_kmp.h"
#include "comm/xlogger/xlogger.h"
#include "xlog/appender.h"
#include "xlog/xlogger_interface.h"

extern "C" {

void Kmp_initLogFile(
        int level, int appendMode,
        const char *cacheDir, const char *logDir,
        const char *namePrefix, const char *pubKey) {
    mars::xlog::XLogConfig config = {
            .mode_ = (mars::xlog::TAppenderMode) appendMode,
            .logdir_ = logDir,
            .nameprefix_ = namePrefix,
            .pub_key_ = pubKey,
            .cachedir_ = cacheDir
    };
    mars::xlog::appender_open(config);
}

void Kmp_setMaxAliveTime(long maxAliveTime) {
    mars::xlog::SetMaxAliveTime(0, maxAliveTime);
}

void Kmp_setConsoleLogOpen(bool open) {
    mars::xlog::SetConsoleLogOpen(0, open);
}

void Kmp_writeLog(int level, const char* tag,
        int pid, int tid, int main_tid, const char* msg) {
    XLoggerInfo xlog_info;
    gettimeofday(&xlog_info.timeval, nullptr);
    xlog_info.level = (TLogLevel)level;
    xlog_info.pid = pid;
    xlog_info.tid = tid;
    xlog_info.maintid = main_tid;
    xlog_info.tag = tag;
    xlog_info.filename = "";
    xlog_info.func_name = "";
    xlog_info.line = 0;
    mars::xlog::XloggerWrite(0, &xlog_info, msg);
}

void Kmp_flush(bool sync) {
    mars::xlog::Flush(0, sync);
}


}

void ExportXlog() {
}