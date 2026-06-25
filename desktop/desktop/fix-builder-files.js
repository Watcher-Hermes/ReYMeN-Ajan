/**
 * fix-builder-files.js
 * package.json'daki build.files array'inden "!node_modules/**" gibi
 * dependency paketlemesini bozan exclude pattern'lerini otomatik kaldirir.
 *
 * Kullanim: package.json ile ayni klasore koy, calistir:
 *   node fix-builder-files.js
 */

const fs = require("fs");
const path = require("path");

const pkgPath = path.join(__dirname, "package.json");
const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf8"));

if (!pkg.build || !Array.isArray(pkg.build.files)) {
  console.log("build.files bulunamadi -> electron-builder.yml kullaniyor olabilirsin, manuel kontrol et.");
  process.exit(1);
}

const badPattern = /^!\s*node_modules\/?\*{0,2}\/?\*{0,1}$/;

const before = pkg.build.files.length;
const removed = pkg.build.files.filter((entry) => badPattern.test(String(entry).trim()));
pkg.build.files = pkg.build.files.filter((entry) => !badPattern.test(String(entry).trim()));
const after = pkg.build.files.length;

if (before === after) {
  console.log("Sorunlu exclude pattern bulunamadi. files array zaten temiz olabilir:");
} else {
  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + "\n");
  console.log("Kaldirildi: " + JSON.stringify(removed));
  console.log("package.json guncellendi. Guncel files array:");
}

console.log(pkg.build.files);
