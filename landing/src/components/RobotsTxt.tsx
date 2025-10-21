import { useEffect } from 'react';
import { useRobots } from '../utils/robots';

export const RobotsTxt: React.FC = () => {
  const { generateRobotsTxt, getDefaultConfig } = useRobots();

  useEffect(() => {
    const content = generateRobotsTxt(getDefaultConfig());
    document.body.innerHTML = `<pre>${content}</pre>`;
    Object.assign(document.body.style, {
      fontFamily: 'monospace',
      fontSize: '14px',
      margin: '0',
      padding: '10px',
      backgroundColor: '#f5f5f5'
    });
  }, [generateRobotsTxt, getDefaultConfig]);

  return null;
};

export default RobotsTxt;