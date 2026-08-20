// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Datacrafter',
  tagline: 'NoSQL-first ETL command-line tool',
  favicon: 'img/favicon.svg',

  url: 'https://apicrafter.github.io',
  baseUrl: '/datacrafter/',

  organizationName: 'apicrafter',
  projectName: 'datacrafter',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/apicrafter/datacrafter/edit/main/docs/docs/',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/logo.svg',
      navbar: {
        title: 'Datacrafter',
        logo: {
          alt: 'Datacrafter logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            to: '/',
            label: 'Contents',
            position: 'left',
            activeBaseRegex: '^/datacrafter/?$',
          },
          {
            type: 'docSidebar',
            sidebarId: 'docs',
            position: 'left',
            label: 'Docs',
          },
          {
            to: '/getting-started/cookbook',
            label: 'Cookbook',
            position: 'left',
          },
          {
            href: 'https://apicrafter.github.io/datacrafter/llms.txt',
            label: 'llms.txt',
            position: 'right',
          },
          {
            href: 'https://github.com/apicrafter/datacrafter',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Contents',
                to: '/',
              },
              {
                label: 'Getting Started',
                to: '/getting-started/installation',
              },
              {
                label: 'CLI Reference',
                to: '/commands/',
              },
              {
                label: 'Configuration',
                to: '/configuration/',
              },
              {
                label: 'Cookbook',
                to: '/getting-started/cookbook',
              },
            ],
          },
          {
            title: 'Pipeline',
            items: [
              {
                label: 'Projects',
                to: '/concepts/projects',
              },
              {
                label: 'Extractors',
                to: '/concepts/extractors',
              },
              {
                label: 'Processors',
                to: '/concepts/processors',
              },
              {
                label: 'Destinations',
                to: '/concepts/destinations',
              },
            ],
          },
          {
            title: 'Project',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/apicrafter/datacrafter',
              },
              {
                label: 'PyPI',
                href: 'https://pypi.org/project/datacrafter/',
              },
              {
                label: 'Changelog',
                href: 'https://github.com/apicrafter/datacrafter/blob/main/CHANGELOG.md',
              },
              {
                label: 'License',
                to: '/license',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Ivan Begtin and contributors. Datacrafter is Apache-2.0 licensed.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'bash', 'yaml', 'json'],
      },
    }),
};

module.exports = config;
