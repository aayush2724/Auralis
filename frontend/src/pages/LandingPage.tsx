import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import LoginModal from '../components/ui/LoginModal';
import { Button } from '../components/ui/Button';
import StatsBar from '../components/landing/StatsBar';
import { useTypewriter } from '../hooks/useTypewriter';

const LandingPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const showLogin = searchParams.get('login') === 'true';
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const prevX = useRef<number | null>(null);
  const targetTime = useRef<number>(0);

  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const serviceOptions = ["Brand", "Digital", "Campaign", "Other"];

  const { displayed, done } = useTypewriter("we'd love to\nhear from you!");

  // Hook 1: Desktop mouse scrubbing
  useEffect(() => {
    if (window.innerWidth < 1024) return;
    const video = videoRef.current;
    if (!video) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (prevX.current === null) {
        prevX.current = e.clientX;
        return;
      }
      const delta = e.clientX - prevX.current;
      targetTime.current += (delta / window.innerWidth) * 0.8 * video.duration;
      targetTime.current = Math.max(0, Math.min(targetTime.current, video.duration));
      video.currentTime = targetTime.current;
      prevX.current = e.clientX;
    };

    const handleSeeked = () => {};

    window.addEventListener('mousemove', handleMouseMove);
    video.addEventListener('seeked', handleSeeked);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      video.removeEventListener('seeked', handleSeeked);
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

  const toggleService = (service: string) => {
    if (selectedServices.includes(service)) {
      setSelectedServices(selectedServices.filter(s => s !== service));
    } else {
      setSelectedServices([...selectedServices, service]);
    }
  };

  return (
    <div className="relative bg-white text-neutral-900 font-sans selection:bg-[#EAECE9] selection:text-[#1C2E1E] antialiased overflow-x-hidden flex flex-col lg:block lg:min-h-screen">
      {showLogin && <LoginModal />}
      
      <div className="order-last lg:order-none relative lg:absolute lg:inset-0 lg:z-0 overflow-hidden pointer-events-none w-full aspect-square md:aspect-video lg:aspect-auto lg:h-full bg-neutral-50 lg:bg-transparent">
        <video
          ref={videoRef}
          muted
          playsInline
          preload="auto"
          className="w-full h-full object-cover object-right lg:object-right-bottom"
        >
          <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260601_110537_3a579fa0-7bbc-4d94-9d25-0e816c7840f5.mp4" type="video/mp4" />
        </video>
      </div>

      {/* NAVBAR */}
      <header className="fixed top-0 inset-x-0 z-10 px-5 sm:px-8 py-4 sm:py-5 flex flex-row justify-between items-center bg-transparent">
        <div className="flex flex-row gap-3">
          <span className="text-[21px] sm:text-[26px] tracking-tight text-auralis-green font-display font-normal select-none">auralis</span>
        </div>
        
        <div className="hidden md:flex flex-row items-center gap-8 text-sm font-sans font-medium text-auralis-mist">
          {['Product', 'Solutions', 'Pricing', 'Resources'].map((item) => (
            <button key={item} className="hover:text-auralis-green transition-colors">{item}</button>
          ))}
        </div>
        
        <Button 
          variant="ghost"
          onClick={() => navigate('/dashboard')}
          className="hidden md:block"
        >
          Login
        </Button>

        <button 
          className="md:hidden relative w-6 h-[16px] flex flex-col justify-between z-20"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
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
            {['Product', 'Solutions', 'Pricing', 'Resources'].map(item => (
              <button key={item} className="text-3xl font-sans font-medium text-auralis-mist hover:text-auralis-green transition-colors">{item}</button>
            ))}
            <Button 
              variant="primary"
              onClick={() => navigate('/dashboard')}
              className="mt-8 text-lg px-8 py-4"
            >
              Login
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* CONTENT LAYER */}
      <div className="relative z-10 flex flex-col order-first lg:order-none w-full bg-white lg:bg-transparent pb-8 lg:pb-0 lg:min-h-screen">
        <main id="spade-hero" className="w-full max-w-7xl mx-auto px-6 py-12 flex-1 flex flex-col justify-center">
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-5xl md:text-6xl lg:text-[76px] font-normal tracking-tight text-black leading-[1.08] mb-8 select-none w-full whitespace-pre-wrap">
              {displayed}
              {!done && (
                <span className="inline-block w-[2px] h-[1.1em] bg-black align-middle ml-[2px] animate-blink" />
              )}
            </h1>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <p className="text-lg md:text-xl text-[#5A635A] leading-relaxed font-normal mb-14 max-w-2xl">
              Whether you have questions, feedback,<br />
              drop us a message and we'll get back to you as soon as possible.
            </p>
          </motion.div>

          <div className="mb-2">
            <h2 className="text-2xl font-medium tracking-tight mb-2">What sort of service?</h2>
            <p className="opacity-85 text-[#738273] mb-8">Select all that apply</p>
          </div>

          <div className="flex flex-wrap gap-3 mb-6">
            {serviceOptions.map((service) => {
              const isActive = selectedServices.includes(service);
              return (
                <motion.button
                  key={service}
                  onClick={() => toggleService(service)}
                  className={`
                    ${isActive 
                      ? 'bg-[#1C2E1E] text-white shadow-md shadow-emerald-950/5' 
                      : 'bg-white text-[#1C2E1E] border border-[#F1F3F1] hover:bg-[#F1F3F1]/55'}
                    px-5 py-2.5 rounded-full font-sans text-sm font-medium transition-all relative
                  `}
                >
                  <span className="flex items-center gap-2">
                    {service}
                    <AnimatePresence>
                      {isActive && (
                        <motion.span
                          initial={{ opacity: 0, scale: 0, width: 0 }}
                          animate={{ opacity: 1, scale: 1, width: 'auto' }}
                          exit={{ opacity: 0, scale: 0, width: 0 }}
                          transition={{ type: "spring", stiffness: 300, damping: 20 }}
                        >
                          <Check size={16} className="text-white" />
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </span>
                </motion.button>
              );
            })}
          </div>

          <AnimatePresence mode="wait">
            {selectedServices.length === 0 ? (
              <motion.p
                key="empty"
                initial={{ opacity: 0 }} 
                animate={{ opacity: 0.5 }} 
                exit={{ opacity: 0 }}
                className="italic text-xs text-[#738273]"
              >
                Please click to select services above.
              </motion.p>
            ) : (
              <motion.div
                key="selected"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-[#FAFBF9] border border-[#F1F3F1] rounded-2xl p-4 flex flex-row justify-between items-center"
              >
                <span className="text-sm text-[#1C2E1E]">
                  Ready to inquire about: {selectedServices.join(', ')}
                </span>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="text-[#4D6D47] uppercase text-xs font-medium hover:opacity-70 transition-opacity"
                >
                  Let's Go →
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            className="mt-8 opacity-40 text-neutral-500 w-full flex justify-start cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => document.getElementById('stats')?.scrollIntoView({ behavior: 'smooth' })}
          >
            <ChevronDown size={20} />
          </motion.div>
        </main>
      </div>

      <StatsBar />
    </div>
  );
};

export default LandingPage;
