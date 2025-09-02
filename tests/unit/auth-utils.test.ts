import { signAccessToken, verifyToken } from '../../src/services/auth';

describe('auth utils', () => {
  test('sign and verify token', () => {
    const token = signAccessToken({ id: 1, tenant_id: 1 });
    const payload: any = verifyToken(token as string);
    expect(payload.id).toBe(1);
    expect(payload.tenant_id).toBe(1);
  });
});
