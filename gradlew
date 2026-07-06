#!/bin/sh
# Gradle startup script for POSIX
DIRNAME="$(cd "$(dirname "$0")" && pwd)"
APP_BASE_NAME=$(basename "$0")
CLASSPATH="$DIRNAME/gradle/wrapper/gradle-wrapper.jar"
JAVACMD="java"
exec "$JAVACMD" -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
