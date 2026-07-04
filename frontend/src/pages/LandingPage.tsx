import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import LoginModal from '../components/ui/LoginModal';
import { Button } from '../components/ui/Button';
import StatsBar from '../components/landing/StatsBar';
import HowItWorks from '../components/landing/HowItWorks';
import Features from '../components/landing/Features';
import Footer from '../components/landing/Footer';

const LandingPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const showLogin = searchParams.get('login') === 'true';
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const prevX = useRef<number | null>(null);
  const targetTime = useRef<number>(0);
  const rafRef = useRef<number | null>(null);
  const pendingTime = useRef<number | null>(null);

  const { scrollYProgress } = useScroll({ target: wrapperRef, offset: ['start start', 'end end'] });

  const videoScale = useTransform(scrollYProgress, [0, 0.20, 0.45, 0.70, 0.88, 1], [1, 1, 2.5, 2.5, 2, 1]);
  const videoOrigin = useTransform(
    scrollYProgress, 
    [0, 0.20, 0.45, 0.70, 0.88, 1], 
    ["75% 40%", "75% 40%", "75% 25%", "60% 65%", "80% 40%", "75% 40%"]
  );

  const stage1And5Opacity = useTransform(scrollYProgress, [0, 0.16, 0.20, 0.88, 0.92, 1], [1, 1, 0, 0, 1, 1]);
  const pointerEvents1And5 = useTransform(scrollYProgress, (v) => (v < 0.2 || v > 0.88) ? "auto" : "none");
  const stage2Opacity = useTransform(scrollYProgress, [0.20, 0.24, 0.41, 0.45], [0, 1, 1, 0]);
  const stage3Opacity = useTransform(scrollYProgress, [0.45, 0.49, 0.66, 0.70], [0, 1, 1, 0]);
  const stage4Opacity = useTransform(scrollYProgress, [0.70, 0.74, 0.84, 0.88], [0, 1, 1, 0]);

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
      <div ref={wrapperRef} className="relative w-full h-[500vh]">
        <div className="sticky top-0 h-screen w-full overflow-hidden flex flex-col lg:block">
          
          <div 
            className="order-last lg:order-none relative lg:absolute lg:inset-0 lg:z-0 overflow-hidden pointer-events-none w-full aspect-square md:aspect-video lg:aspect-auto lg:h-full bg-neutral-50 lg:bg-transparent"
            style={{ transform: 'translateZ(0)' }}
          >
            <motion.video
              ref={videoRef}
              muted
              playsInline
              preload="auto"
              poster="/src/assets/hero.png"
              className="w-full h-full object-cover object-right lg:object-right-bottom will-change-transform"
              style={{ scale: videoScale, transformOrigin: videoOrigin as any }}
            >
              <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260601_110537_3a579fa0-7bbc-4d94-9d25-0e816c7840f5.mp4" type="video/mp4" />
              <div className="w-full h-full bg-[#f9fafb] flex items-center justify-center">
                <img
                  src="/src/assets/hero.png"
                  alt="Auralis AI assistant"
                  className="w-full h-full object-cover object-right"
                />
              </div>
            </motion.video>
          </div>

          {/* CONTENT LAYER */}
          <div className="relative z-10 flex flex-col order-first lg:order-none w-full h-full bg-white lg:bg-transparent pb-8 lg:pb-0">
            <main id="spade-hero" className="relative w-full max-w-7xl mx-auto px-6 h-full flex flex-col justify-center">
              
              {/* STAGE 1 & 5 */}
              <motion.div
                style={{ opacity: stage1And5Opacity, pointerEvents: pointerEvents1And5 as any }}
                className="absolute inset-x-6 top-1/2 -translate-y-1/2 flex flex-col items-start max-w-lg"
              >
                <span className="text-[#dd6668] font-sans tracking-wide uppercase text-sm font-semibold mb-4">
                  AI SALES INTELLIGENCE
                </span>
                <h1 className="font-display text-[52px] lg:text-[76px] text-[#0a0a0a] leading-[1.08] mb-6">
                  Turn every objection<br />into a closed deal.
                </h1>
                <p className="font-sans text-xl text-[#6b7280] leading-relaxed">
                  Auralis reads the room in real time — classifying objections, adapting to buyer
                  personas, and knowing exactly when to bring in a human.
                </p>
                <div className="flex flex-row items-center gap-4 mt-10 pointer-events-auto">
                  <button 
                    onClick={() => navigate('/?login=true')}
                    className="bg-[#dd6668] text-white px-7 py-3.5 rounded-full font-sans font-medium text-sm hover:bg-[#c45557] transition-colors"
                  >
                    Try it now
                  </button>
                  <button 
                    onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                    className="text-[#dd6668] font-sans font-medium text-sm underline underline-offset-4 hover:opacity-70 transition-opacity"
                  >
                    See how it works
                  </button>
                </div>
              </motion.div>

              {/* STAGE 2 */}
              <motion.div
                style={{ opacity: stage2Opacity }}
                className="absolute inset-x-6 top-1/2 -translate-y-1/2 flex flex-col items-start max-w-lg pointer-events-none"
              >
                <span className="text-[#dd6668] font-sans tracking-wide uppercase text-sm font-semibold mb-4">
                  OBJECTION CLASSIFICATION
                </span>
                <h2 className="font-display text-[52px] lg:text-[76px] text-[#0a0a0a] leading-[1.08] mb-6">
                  Every objection,<br />instantly understood.
                </h2>
                <p className="font-sans text-xl text-[#6b7280] leading-relaxed">
                  Price. Trust. Timing. Competitor. Fit. Auralis classifies
                  objection type in under 2 seconds and routes it to the right
                  playbook automatically.
                </p>
              </motion.div>

              {/* STAGE 3 */}
              <motion.div
                style={{ opacity: stage3Opacity }}
                className="absolute inset-x-6 top-1/2 -translate-y-1/2 flex flex-col items-start max-w-lg pointer-events-none"
              >
                <span className="text-[#dd6668] font-sans tracking-wide uppercase text-sm font-semibold mb-4">
                  BUYER PERSONA DETECTION
                </span>
                <h2 className="font-display text-[52px] lg:text-[76px] text-[#0a0a0a] leading-[1.08] mb-6">
                  Knows who it's<br />talking to.
                </h2>
                <p className="font-sans text-xl text-[#6b7280] leading-relaxed">
                  Auralis identifies the prospect's role and communication
                  style so every response feels like it was written for them
                  specifically — not generated.
                </p>
              </motion.div>

              {/* STAGE 4 */}
              <motion.div
                style={{ opacity: stage4Opacity }}
                className="absolute inset-x-6 top-1/2 -translate-y-1/2 flex flex-col items-start max-w-lg pointer-events-none"
              >
                <span className="text-[#dd6668] font-sans tracking-wide uppercase text-sm font-semibold mb-4">
                  SMART HANDOFF
                </span>
                <h2 className="font-display text-[52px] lg:text-[76px] text-[#0a0a0a] leading-[1.08] mb-6">
                  Knows when to<br />step aside.
                </h2>
                <p className="font-sans text-xl text-[#6b7280] leading-relaxed">
                  When confidence drops or frustration spikes, Auralis flags
                  for human takeover before the deal is at risk. No dropped
                  conversations, no awkward moments.
                </p>
              </motion.div>

              <motion.div
                animate={{ y: [0, 8, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                className="absolute bottom-12 left-6 opacity-40 text-neutral-500 flex justify-start cursor-pointer hover:opacity-80 transition-opacity z-20 pointer-events-auto"
                onClick={() => document.getElementById('stats')?.scrollIntoView({ behavior: 'smooth' })}
              >
                <ChevronDown size={20} />
              </motion.div>

            </main>
          </div>
        </div>
      </div>

      <HowItWorks />
      <StatsBar />
      <Features />
      <Footer />
    </div>
  );
};

export default LandingPage;
