import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useSearchParams } from 'react-router-dom';
import LoginModal from '../components/ui/LoginModal';
import { Button } from '../components/ui/Button';
import StatsBar from '../components/landing/StatsBar';
import HowItWorks from '../components/landing/HowItWorks';
import RobotFeatures from '../components/landing/RobotFeatures';
import Features from '../components/landing/Features';
import Footer from '../components/landing/Footer';

const LandingPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const showLogin = searchParams.get('login') === 'true';
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const prevX = useRef<number | null>(null);
  const targetTime = useRef<number>(0);
  const rafRef = useRef<number | null>(null);
  const pendingTime = useRef<number | null>(null);

  // Hook 1: Desktop mouse scrubbing
  useEffect(() => {
    if (window.innerWidth < 1024) return;
    const video = videoRef.current;
    if (!video) return;

    const tick = () => {
      if (pendingTime.current !== null && !video.seeking) {
        video.currentTime = pendingTime.current;
        pendingTime.current = null;
      }
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);

    const handleMouseMove = (e: MouseEvent) => {
      if (prevX.current === null) { prevX.current = e.clientX; return; }
      const delta = e.clientX - prevX.current;
      targetTime.current = Math.max(
        0,
        Math.min(
          targetTime.current + (delta / window.innerWidth) * 0.8 * video.duration,
          video.duration
        )
      );
      pendingTime.current = targetTime.current;
      prevX.current = e.clientX;
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  // Hook 2: Mobile autoplay
  useEffect(() => {
    if (window.innerWidth >= 1024) return;
    const video = videoRef.current;
    if (!video) return;
    video.autoplay = true;
    video.play().catch(() => {});
  }, []);



  return (
    <div className="relative bg-white text-neutral-900 font-sans selection:bg-[#f9fafb] selection:text-[#0a0a0a] antialiased flex flex-col">
      {showLogin && <LoginModal />}
      
      {/* NAVBAR */}
      <header className="fixed top-0 inset-x-0 z-10 px-5 sm:px-8 py-4 sm:py-5 flex flex-row justify-between items-center bg-transparent">
        <div className="flex flex-row gap-3">
          <span className="text-[21px] sm:text-[26px] tracking-tight text-[#0a0a0a] font-display font-normal select-none">auralis</span>
        </div>
        
        <div className="hidden md:flex flex-row items-center gap-8 text-sm font-sans font-medium text-[#6b7280]">
          {[
            { name: 'Product', id: 'features' },
            { name: 'Solutions', id: 'how-it-works' },
            { name: 'Pricing', id: 'footer' },
            { name: 'Resources', id: 'how-it-works' }
          ].map((item) => (
            <button 
              key={item.name} 
              onClick={() => document.getElementById(item.id)?.scrollIntoView({ behavior: 'smooth' })}
              className="hover:text-[#0a0a0a] transition-colors"
            >
              {item.name}
            </button>
          ))}
        </div>
        
        <Button 
          variant="ghost"
          onClick={() => navigate('/?login=true')}
          className="hidden md:block"
        >
          Login
        </Button>

        <button 
          className="md:hidden relative w-6 h-[16px] flex flex-col justify-between z-20"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={isMobileMenuOpen}
        >
          <span className={`w-6 h-[2px] bg-black transition-all duration-300 origin-center ${isMobileMenuOpen ? 'rotate-45 translate-y-[7px]' : ''}`} />
          <span className={`w-6 h-[2px] bg-black transition-all duration-300 ${isMobileMenuOpen ? 'opacity-0' : ''}`} />
          <span className={`w-6 h-[2px] bg-black transition-all duration-300 origin-center ${isMobileMenuOpen ? '-rotate-45 -translate-y-[7px]' : ''}`} />
        </button>
      </header>

      {/* MOBILE OVERLAY */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[9] bg-white/95 backdrop-blur-sm flex flex-col items-center justify-center space-y-8 pointer-events-auto"
          >
            {[
              { name: 'Product', id: 'features' },
              { name: 'Solutions', id: 'how-it-works' },
              { name: 'Pricing', id: 'footer' },
              { name: 'Resources', id: 'how-it-works' }
            ].map(item => (
              <button 
                key={item.name} 
                onClick={() => {
                  setIsMobileMenuOpen(false);
                  document.getElementById(item.id)?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="text-3xl font-sans font-medium text-[#6b7280] hover:text-[#0a0a0a] transition-colors"
              >
                {item.name}
              </button>
            ))}
            <Button 
              variant="primary"
              onClick={() => navigate('/?login=true')}
              className="mt-8 text-lg px-8 py-4"
            >
              Login
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* HERO SCROLL WRAPPER */}
  <div className="relative min-h-screen overflow-hidden bg-white">

    {/* Video — right side, same container as before */}
    <div
      className="absolute inset-0 lg:z-0 overflow-hidden pointer-events-none"
      style={{ transform: 'translateZ(0)' }}
    >
      <video
        ref={videoRef}
        muted
        playsInline
        preload="auto"
        className="w-full h-full object-cover object-right
                   lg:object-right-bottom will-change-transform"
      >
        <source
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260601_110537_3a579fa0-7bbc-4d94-9d25-0e816c7840f5.mp4"
          type="video/mp4"
        />
      </video>
    </div>

    {/* Static hero text — left side */}
    <div className="relative z-10 h-full min-h-screen flex flex-col
                    justify-center px-6 max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="max-w-lg"
      >
        <span className="text-[#dd6668] font-sans tracking-wide uppercase
                         text-sm font-semibold mb-4 block">
          AI SALES INTELLIGENCE
        </span>
        <h1 className="font-display text-[52px] lg:text-[76px] text-[#0a0a0a]
                       leading-[1.08] mb-6">
          Turn every objection<br />into a closed deal.
        </h1>
        <p className="font-sans text-xl text-[#6b7280] leading-relaxed mb-10">
          Auralis reads the room in real time — classifying objections,
          adapting to buyer personas, and knowing exactly when to bring
          in a human.
        </p>
        <div className="flex flex-row items-center gap-4">
          <button
            onClick={() => navigate('/?login=true')}
            className="bg-[#dd6668] text-white px-7 py-3.5 rounded-full
                       font-sans font-medium text-sm hover:bg-[#c45557]
                       transition-colors"
          >
            Try it now
          </button>
          <button
            onClick={() =>
              document.getElementById('how-it-works')
                ?.scrollIntoView({ behavior: 'smooth' })
            }
            className="text-[#dd6668] font-sans font-medium text-sm
                       underline underline-offset-4 hover:opacity-70
                       transition-opacity"
          >
            See how it works
          </button>
        </div>
      </motion.div>
    </div>
  </div>

      <HowItWorks />
      <RobotFeatures />
      <StatsBar />
      <Features />
      <Footer />
    </div>
  );
};

export default LandingPage;
