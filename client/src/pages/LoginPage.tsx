import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, Mic, ArrowLeft } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useLogin } from '../api/hooks/useAuth';
import { Button } from '../components/ui/Button';

export default function LoginPage() {
  const navigate = useNavigate();
  const loginMutation = useLogin();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    loginMutation.mutate(formData, {
      onSuccess: () => {
        navigate('/dashboard', { replace: true });
      },
    });
  };

  return (
    <div className="min-h-screen bg-[#fafbfa] text-[#0a0a0a]">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl items-center px-6 py-10">
        <div className="grid w-full gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="hidden flex-col justify-between rounded-[2rem] border border-[#f1f3f1] bg-white p-10 shadow-sm lg:flex">
            <Link to="/" className="inline-flex w-fit items-center gap-2 text-sm font-medium text-[#6b7280] transition-colors hover:text-[#0a0a0a]">
              <ArrowLeft className="h-4 w-4" />
              Back to home
            </Link>
            <div>
              <p className="mb-4 text-xs font-semibold uppercase tracking-[0.3em] text-[#dd6668]">Auralis Login</p>
              <h1 className="font-display text-5xl leading-[1.05] tracking-tight text-[#0a0a0a]">
                Sign in to continue the conversation.
              </h1>
              <p className="mt-5 max-w-lg text-lg leading-relaxed text-[#6b7280]">
                Access your workspace, review conversations, and keep the handoff flow moving.
              </p>
            </div>
            <div className="flex items-center gap-3 text-sm text-[#6b7280]">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#dd6668] to-[#0a0a0a] text-white">
                <Mic className="h-5 w-5" />
              </span>
              Secure access for the sales team.
            </div>
          </div>

          <div className="flex items-center justify-center">
            <motion.div
              initial={{ opacity: 0, y: 16, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
              className="w-full max-w-md rounded-[2rem] border border-[#f1f3f1] bg-white p-8 shadow-[0_24px_80px_rgba(0,0,0,0.08)]"
            >
              <div className="mb-8 flex flex-col items-center text-center">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#dd6668] to-[#0a0a0a] text-white">
                  <Mic className="h-6 w-6" />
                </div>
                <h2 className="font-display text-2xl font-normal tracking-tight text-[#0a0a0a]">Welcome back</h2>
                <p className="mt-1 text-sm font-light text-[#6b7280]">Sign in to your workspace</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="login-email" className="mb-1 block text-xs font-medium uppercase tracking-widest text-[#0a0a0a]">Email</label>
                  <input
                    id="login-email"
                    type="email"
                    required
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="w-full rounded-xl border border-[#f1f3f1] px-4 py-3 font-sans text-[#0a0a0a] outline-none transition-colors focus:border-[#dd6668] focus:ring-4 focus:ring-[#dd6668]/10"
                  />
                </div>

                <div>
                  <label htmlFor="login-password" className="mb-1 block text-xs font-medium uppercase tracking-widest text-[#0a0a0a]">Password</label>
                  <input
                    id="login-password"
                    type="password"
                    required
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    className="w-full rounded-xl border border-[#f1f3f1] px-4 py-3 font-sans text-[#0a0a0a] outline-none transition-colors focus:border-[#dd6668] focus:ring-4 focus:ring-[#dd6668]/10"
                  />
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  disabled={loginMutation.isPending}
                  className="mt-2 w-full justify-center"
                >
                  {loginMutation.isPending ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Signing in...</span>
                    </>
                  ) : (
                    <span>Sign In</span>
                  )}
                </Button>

                <AnimatePresence>
                  {loginMutation.isError && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600"
                    >
                      Invalid credentials. Please try again.
                    </motion.div>
                  )}
                </AnimatePresence>
              </form>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}