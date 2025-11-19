const rollup = require('rollup');
const resolve = require('@rollup/plugin-node-resolve');
const commonjs = require('@rollup/plugin-commonjs');
const terser = require('rollup-plugin-terser').terser;

const plugins = [
    resolve({ preferBuiltins: true }),
    commonjs(),
    terser(),
];

// Define external dependencies to avoid bundling them
const external = [
    '@tiptap/core',
    '@tiptap/starter-kit',
    '@tiptap/extension-link',
    '@tiptap/extension-image',
    '@tiptap/extension-youtube',
    '@tiptap/pm', // Common dependency of TipTap packages
    '@tiptap/pm/state',
    '@tiptap/pm/model',
    '@tiptap/pm/transform',
    '@tiptap/pm/view',
    '@tiptap/pm/schema-list',
    '@tiptap/pm/dropcursor',
    '@tiptap/pm/gapcursor',
    '@tiptap/pm/history',
    '@tiptap/pm/commands',
    '@tiptap/pm/keymap',
];

const builds = [
    {
        input: './node_modules/@tiptap/core/src/index.js',
        output: './dist/tiptap.min.js',
    },
    {
        input: './node_modules/@tiptap/starter-kit/src/index.js',
        output: './dist/starter-kit.min.js',
    },
    {
        input: './node_modules/@tiptap/extension-link/src/index.js',
        output: './dist/link.min.js',
    },
    {
        input: './node_modules/@tiptap/extension-image/src/index.js',
        output: './dist/image.min.js',
    },
    {
        input: './node_modules/@tiptap/extension-youtube/src/index.js',
        output: './dist/youtube.min.js',
    },
];

async function build(input, output) {
    try {
        const bundle = await rollup.rollup({
            input: input,
            plugins: plugins,
            external: external,
        });

        await bundle.write({
            file: output,
            format: 'umd',
            name: input.split('/').pop().replace('.js', ''),
            globals: {
                '@tiptap/core': 'TipTap',
                '@tiptap/starter-kit': 'TipTap.StarterKit',
                '@tiptap/extension-link': 'TipTap.Link',
                '@tiptap/extension-image': 'TipTap.Image',
                '@tiptap/extension-youtube': 'TipTap.Youtube',
                '@tiptap/pm': 'TipTap.PM',
                '@tiptap/pm/state': 'TipTap.PM.State',
                '@tiptap/pm/model': 'TipTap.PM.Model',
                '@tiptap/pm/transform': 'TipTap.PM.Transform',
                '@tiptap/pm/view': 'TipTap.PM.View',
                '@tiptap/pm/schema-list': 'TipTap.PM.SchemaList',
                '@tiptap/pm/dropcursor': 'TipTap.PM.DropCursor',
                '@tiptap/pm/gapcursor': 'TipTap.PM.GapCursor',
                '@tiptap/pm/history': 'TipTap.PM.History',
                '@tiptap/pm/commands': 'TipTap.PM.Commands',
                '@tiptap/pm/keymap': 'TipTap.PM.Keymap',
            },
        });

        await bundle.close();
    } catch (error) {
        console.error(`Failed to build ${input}:`, error);
        throw error;
    }
}

async function runBuilds() {
    for (const { input, output } of builds) {
        console.log(`Building ${input} to ${output}`);
        await build(input, output);
    }
    console.log('Build completed');
}

runBuilds().catch(err => {
    console.error(err);
    process.exit(1);
});