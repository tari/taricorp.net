'use strict';

const del = require('del');
const closure = require('google-closure-compiler-js').gulp();
const cssnano = require('gulp-cssnano');
const eslint = require('gulp-eslint');
const gulp = require('gulp');
const htmlmin = require('gulp-htmlmin');
const runSequence = require('run-sequence');

const out = './public-min/'

// Copy Hugo's output into a new directory and selectively minify into the new
// directory.
gulp.task('default', ['copy'], function() {
    return gulp.start(['html', 'css', 'js']);
});

gulp.task('clean', function() {
    return del([out + '**']);
});

gulp.task('clean-hugo', function() {
    return del(['./public/**']);
});

gulp.task('copy', function() {
    return gulp.src('public/**/*').pipe(gulp.dest(out));
});

gulp.task('html', function() {
    return gulp.src('public/**/*.html')
               .pipe(htmlmin({collapseWhitespace: true}))
               .pipe(gulp.dest(out));
});

gulp.task('css', function() {
    return gulp.src('public/css/**/*.css')
               .pipe(cssnano())
               .pipe(gulp.dest(out + 'css/'));
});

gulp.task('jslint', function() {
    return gulp.src(['static/js/**/*.js'])
               .pipe(eslint())
               .pipe(eslint.format())
               .pipe(eslint.failAfterError());
});

gulp.task('js', ['jslint'], function() {
    return gulp.src('public/js/**/*.js')
               .pipe(closure({
                   compilationLevel: 'SIMPLE',
                   warningLevel: 'VERBOSE',
                   createSourceMap: true,
               }))
               .pipe(gulp.dest(out + 'js/'));
});
