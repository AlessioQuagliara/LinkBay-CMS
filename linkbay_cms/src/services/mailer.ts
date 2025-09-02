export async function sendMail(opts: { to: string; subject: string; text?: string; html?: string }) {
  // placeholder - integrate nodemailer or external provider
  console.log('sendMail', opts);
}
