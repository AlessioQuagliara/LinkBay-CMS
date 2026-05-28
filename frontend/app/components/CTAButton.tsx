'use client';

interface CTAButtonProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'register' | 'login';
}

const AGENCY_REGISTER_URL =
  process.env.NEXT_PUBLIC_AGENCY_REGISTER_URL ?? 'http://api.localhost/agency/register';

const AGENCY_LOGIN_URL =
  process.env.NEXT_PUBLIC_AGENCY_LOGIN_URL ?? 'http://api.localhost/linkbay-admin';

export function CTAButton({ children, className = '', variant = 'register' }: CTAButtonProps) {
  const href = variant === 'login' ? AGENCY_LOGIN_URL : AGENCY_REGISTER_URL;

  return (
    <a href={href} className={className}>
      {children}
    </a>
  );
}

export const agencyRegisterUrl = AGENCY_REGISTER_URL;
export const agencyLoginUrl = AGENCY_LOGIN_URL;
