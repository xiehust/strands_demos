'use client';

import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
  AppLayout as CloudscapeAppLayout,
  TopNavigation,
  SideNavigation,
  SideNavigationProps,
} from '@cloudscape-design/components';

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [navigationOpen, setNavigationOpen] = useState(true);

  const navigationItems: SideNavigationProps.Item[] = [
    {
      type: 'link',
      text: 'Remote Agents',
      href: '/remote-agents',
    },
    {
      type: 'link',
      text: 'Chat',
      href: '/chat',
    },
  ];

  return (
    <>
      <TopNavigation
        identity={{
          href: '/',
          title: 'A2A Demo UI',
        }}
        utilities={[
          {
            type: 'button',
            text: 'Settings',
            href: '#',
            external: false,
          },
        ]}
      />
      <CloudscapeAppLayout
        navigation={
          <SideNavigation
            activeHref={pathname}
            header={{ href: '/', text: 'Navigation' }}
            items={navigationItems}
            onFollow={(event) => {
              if (!event.detail.external) {
                event.preventDefault();
                router.push(event.detail.href);
              }
            }}
          />
        }
        navigationOpen={navigationOpen}
        onNavigationChange={({ detail }) => setNavigationOpen(detail.open)}
        content={children}
        toolsHide
      />
    </>
  );
}