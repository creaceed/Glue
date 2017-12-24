#!/bin/sh

BUILD_DIR=build
ZIP_FILE=glue.zip
BIN_DIR=bin
BIN_FILE=$BIN_DIR/glue

rm -fr $BUILD_DIR
mkdir $BUILD_DIR
cp -R hjson $BUILD_DIR/
cp *.py $BUILD_DIR/
cd $BUILD_DIR
zip -r ../$ZIP_FILE *
cd -
mkdir -p $BIN_DIR
echo '#!/usr/bin/python' | cat - $ZIP_FILE > $BIN_FILE
chmod +x $BIN_FILE
rm -fr $BUILD_DIR $ZIP_FILE