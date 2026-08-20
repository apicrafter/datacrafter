import React from 'react';
import Link from '@docusaurus/Link';
import styles from './DocsContents.module.css';

const sections = [
  {
    title: 'Getting Started',
    to: '/getting-started/installation',
    description:
      'Install Datacrafter and run a first extract → process → load pipeline.',
    links: [
      {label: 'Installation', to: '/getting-started/installation'},
      {label: 'Quick start', to: '/getting-started/quick-start'},
      {label: 'When to use', to: '/getting-started/when-to-use'},
      {label: 'Cookbook', to: '/getting-started/cookbook'},
      {label: 'Troubleshooting', to: '/getting-started/troubleshooting'},
    ],
  },
  {
    title: 'Concepts',
    to: '/concepts/projects',
    description:
      'How YAML projects, extractors, processors, and destinations fit together.',
    links: [
      {label: 'Projects', to: '/concepts/projects'},
      {label: 'What is NoSQL ETL?', to: '/concepts/etl'},
      {label: 'Extractors', to: '/concepts/extractors'},
      {label: 'Processors', to: '/concepts/processors'},
      {label: 'Destinations', to: '/concepts/destinations'},
    ],
  },
  {
    title: 'Use Cases',
    to: '/use-cases/csv-to-jsonl',
    description:
      'End-to-end recipes for CSV, Excel, ZIP+XML, catalogs, and databases.',
    links: [
      {label: 'CSV to JSONL', to: '/use-cases/csv-to-jsonl'},
      {label: 'Excel registries', to: '/use-cases/excel-registries'},
      {label: 'ZIP+XML open data', to: '/use-cases/zip-xml-opendata'},
      {label: 'Catalogs and feeds', to: '/use-cases/catalogs-and-feeds'},
      {label: 'Document stores', to: '/use-cases/databases'},
    ],
  },
  {
    title: 'CLI Reference',
    to: '/commands/',
    description:
      'Command-by-command reference for init, run, inspect, and config.',
    links: [
      {label: 'All commands', to: '/commands/'},
      {label: 'init', to: '/commands/init'},
      {label: 'run', to: '/commands/run'},
      {label: 'check', to: '/commands/check'},
      {label: 'schema / metrics', to: '/commands/schema'},
      {label: 'config', to: '/commands/config'},
    ],
  },
  {
    title: 'Configuration',
    to: '/configuration/',
    description:
      'datacrafter.yml schema, extractors, processors, destinations, and trust model.',
    links: [
      {label: 'YAML schema', to: '/configuration/'},
      {label: 'Extractors', to: '/configuration/extractors'},
      {label: 'Processors', to: '/configuration/processors'},
      {label: 'Destinations', to: '/configuration/destinations'},
      {label: 'Security', to: '/configuration/security'},
    ],
  },
  {
    title: 'Development',
    to: '/development/contributing',
    description: 'Contributing, community, and license.',
    links: [
      {label: 'Contributing', to: '/development/contributing'},
      {label: 'Community', to: '/development/community'},
      {label: 'License', to: '/license'},
    ],
  },
];

function Section({title, to, description, links}) {
  return (
    <article className={styles.card}>
      <h3 className={styles.cardTitle}>
        <Link to={to}>{title}</Link>
      </h3>
      <p className={styles.cardDescription}>{description}</p>
      <ul className={styles.linkList}>
        {links.map((item) => (
          <li key={item.label}>
            {item.href ? (
              <a href={item.href}>{item.label}</a>
            ) : (
              <Link to={item.to}>{item.label}</Link>
            )}
          </li>
        ))}
      </ul>
    </article>
  );
}

export default function DocsContents() {
  return (
    <section className={styles.contents}>
      <div className="container">
        <h2 className={styles.heading}>Documentation contents</h2>
        <p className={styles.intro}>
          Start with a section below, or use the sidebar from any page. Pipelines
          are declared in <code>datacrafter.yml</code> and run with the{' '}
          <code>datacrafter</code> CLI.
        </p>
        <div className={styles.grid}>
          {sections.map((section) => (
            <Section key={section.title} {...section} />
          ))}
        </div>
      </div>
    </section>
  );
}
