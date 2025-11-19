import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import { terser } from 'rollup-plugin-terser';
import typescript from 'rollup-plugin-typescript2';

export default {
    input: 'index.js', // Overridden by CLI
    output: [
        { file: 'dist/index.cjs', format: 'cjs' },
        { file: 'dist/index.js', format: 'es' },
        { file: 'dist/index.umd.js', format: 'umd', name: 'TipTap', globals: { /* ... */ } },
    ],
    plugins: [
        resolve({ extensions: ['.ts', '.js'] }),
        commonjs(),
        typescript({
            tsconfigOverride: {
                compilerOptions: {
                    target: 'esnext',
                    module: 'esnext',
                    strict: false,
                    esModuleInterop: true,
                    moduleResolution: 'node',
                    declaration: false,
                    noEmitOnError: false
                },
                include: ['node_modules/@tiptap/core/**/*.ts'],
                exclude: ['node_modules/@tiptap/core/dist/**/*']
            },
            useTsconfigDeclarationDir: false,
            check: false // Disable type checking to ignore TS errors
        }),
        terser(),
    ],
    include: ['node_modules/@tiptap/**/*.ts'],
    external: [
        '@tiptap/pm',
        '@tiptap/pm/state',
        '@tiptap/pm/model',
        '@tiptap/pm/transform',
        '@tiptap/pm/view',
        '@tiptap/core',
        '@tiptap/starter-kit',
        '@tiptap/extension-link',
        '@tiptap/extension-image',
        '@tiptap/extension-youtube',
        '@tiptap/pm/schema-list',
        '@tiptap/pm/dropcursor',
        '@tiptap/pm/gapcursor',
        '@tiptap/pm/history',
        '@tiptap/pm/commands',
        '@tiptap/pm/keymap',
    ],
};