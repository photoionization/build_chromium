#!/usr/bin/env node

const cp = require('node:child_process')
const fs = require('node:fs')
const path = require('node:path')

const depotToolsDir = path.join(__dirname, 'vendor/depot_tools')
const buildToolsDir = path.join(__dirname, 'vendor/build_tools')

if (process.platform == 'win32') {
  // build-tools requires python3.bat to be present, so bootstrap the python
  // binary in depot_tools, and add depot_tools to PATH.
  cp.execSync(path.join(depotToolsDir, 'bootstrap/win_tools.bat'))
  process.env.PATH = [ depotToolsDir, process.env.PATH ].join(path.delimiter)
}

const thirdPartyDir = path.join(buildToolsDir, 'third_party')
if (!fs.existsSync(thirdPartyDir))
  fs.mkdirSync(thirdPartyDir)

const nodeModulesDir = path.join(buildToolsDir, 'node_modules')
if (!fs.existsSync(nodeModulesDir)) {
  fs.mkdirSync(nodeModulesDir)
  cp.execSync('yarn', {cwd: nodeModulesDir})
}

const reclient = require(path.join(buildToolsDir, 'src/utils/reclient'))
reclient.downloadAndPrepare({})
if (process.argv.length > 2) {
  cp.execFileSync(reclient.helperPath({}), process.argv.slice(2), {stdio: 'inherit'})
  process.exit(0)
}
