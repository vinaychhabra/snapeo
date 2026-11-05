// Minifies src/style.css and build/app.pre.js into assets/*.min.* (called by build.py)
const fs = require('fs'), csso = require('csso'), { minify } = require('terser');
(async () => {
  const usage = JSON.parse(fs.readFileSync('build/usage.json', 'utf8'));
  const css = csso.minify(fs.readFileSync('src/style.css', 'utf8'), { usage, restructure: true }).css;
  fs.writeFileSync('assets/style.min.css', css);
  const out = await minify(fs.readFileSync('build/app.pre.js', 'utf8'), {
    compress: { passes: 2, ecma: 2020 }, mangle: { toplevel: true }, format: { comments: false }
  });
  fs.writeFileSync('assets/app.min.js', out.code);
  console.log('css', css.length, 'js', out.code.length);
})();
