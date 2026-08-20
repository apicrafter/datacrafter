/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docs: [
    {
      type: 'link',
      label: 'Contents',
      href: '/',
    },
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/when-to-use',
        'getting-started/cookbook',
        'getting-started/troubleshooting',
      ],
    },
    {
      type: 'category',
      label: 'Concepts',
      items: [
        'concepts/projects',
        'concepts/etl',
        'concepts/extractors',
        'concepts/processors',
        'concepts/destinations',
      ],
    },
    {
      type: 'category',
      label: 'Use Cases',
      items: [
        'use-cases/csv-to-jsonl',
        'use-cases/excel-registries',
        'use-cases/zip-xml-opendata',
        'use-cases/catalogs-and-feeds',
        'use-cases/databases',
      ],
    },
    {
      type: 'category',
      label: 'CLI Reference',
      items: [
        'commands/index',
        'commands/init',
        'commands/run',
        'commands/check',
        'commands/status',
        'commands/log',
        'commands/clean',
        'commands/schema',
        'commands/metrics',
        'commands/config',
        'commands/version',
      ],
    },
    {
      type: 'category',
      label: 'Configuration',
      items: [
        'configuration/index',
        'configuration/extractors',
        'configuration/processors',
        'configuration/destinations',
        'configuration/security',
      ],
    },
    {
      type: 'category',
      label: 'Development',
      items: [
        'development/contributing',
        'development/community',
      ],
    },
    'license',
  ],
};

module.exports = sidebars;
