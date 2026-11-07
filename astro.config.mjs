import { readFileSync } from 'node:fs';
import { satteri } from '@astrojs/markdown-satteri';
import starlight from '@astrojs/starlight';
import { defineConfig } from 'astro/config';
import { parse } from 'yaml';

const { chapters } = parse(readFileSync(new URL('./authoring/outline.yaml', import.meta.url), 'utf8'));

// Lessons stay plain Markdown, so the site-only differences are applied here.
const bookMarkdown = {
	name: 'book-markdown',
	// Starlight prints the frontmatter title as the H1.
	heading(node, ctx) {
		if (node.depth === 1) ctx.removeNode(node);
	},
	// Pages are served as folders, so x.md is one level deeper as a URL, except index.md.
	link(node, ctx) {
		const match = node.url.match(/^([^:]*?)\.md(#.*)?$/);
		if (!match) return;
		const up = ctx.fileURL.pathname.endsWith('/index.md') ? '' : '../';
		ctx.setProperty(node, 'url', `${up}${match[1]}/${match[2] ?? ''}`);
	},
};

export default defineConfig({
	site: 'https://armenia-drivers-manual.ygnmehr.workers.dev',
	markdown: { processor: satteri({ mdastPlugins: [bookMarkdown] }) },
	redirects: { '/': '/en/' },
	integrations: [
		starlight({
			title: { en: "Unofficial Armenia Driver's Manual", fa: 'راهنمای غیررسمی رانندگی ارمنستان' },
			customCss: ['./src/book.css'],
			defaultLocale: 'en',
			locales: {
				en: { label: 'English', lang: 'en' },
				fa: { label: 'فارسی', lang: 'fa', dir: 'rtl' },
			},
			sidebar: chapters.map((chapter) => ({
				label: chapter.en,
				translations: { fa: chapter.fa },
				collapsed: true,
				items: [{ autogenerate: { directory: chapter.id } }],
			})),
		}),
	],
});
