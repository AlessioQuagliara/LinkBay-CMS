import { Request, Response } from 'express';

const home = (req: Request, res: Response) => {
  res.render('landing/home', { title: 'LinkBay CMS' });
};

const register = async (req: Request, res: Response) => {
  // placeholder: implement tenant-aware registration here
  const { email } = req.body;
  return res.json({ ok: true, email });
};

export default { home, register };
