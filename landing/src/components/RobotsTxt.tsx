import React, { useEffect, useState } from 'react';
import { useRobots } from '../utils/robots';

export const RobotsTxt: React.FC = () => {
  const [robotsContent, setRobotsContent] = useState<string>('');
  const { generateRobotsTxt, getDefaultConfig } = useRobots();

  useEffect(() => {
    try {
      const config = getDefaultConfig();
      const content = generateRobotsTxt(config);
      setRobotsContent(content);
    } catch (error) {
      console.error('Error generating robots.txt:', error);
      setRobotsContent('User-agent: *\nDisallow: /\n');
    }
  }, [generateRobotsTxt, getDefaultConfig]);

  // Render come plain text
  useEffect(() => {
    if (robotsContent) {
      document.body.innerHTML = `<pre>${robotsContent}</pre>`;
      document.body.style.fontFamily = 'monospace';
      document.body.style.fontSize = '14px';
      document.body.style.margin = '0';
      document.body.style.padding = '10px';
      document.body.style.backgroundColor = '#f5f5f5';
    }
  }, [robotsContent]);

  return null; // Il rendering avviene tramite DOM manipulation
};

export default RobotsTxt;