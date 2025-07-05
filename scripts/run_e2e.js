#!/usr/bin/env node
try {
  require.resolve('@playwright/test');
} catch (err) {
  console.log('Playwright not installed; skipping e2e tests.');
  process.exit(0);
}
const { spawn } = require('child_process');
const child = spawn('npx', ['playwright', 'test'], { stdio: 'inherit' });
child.on('exit', code => process.exit(code));
