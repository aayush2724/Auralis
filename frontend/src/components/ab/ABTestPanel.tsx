
import { motion } from 'framer-motion';
import { Crown, AlertCircle, ArrowUpRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, LabelList } from 'recharts';
import { useABTestResults } from '../../api/hooks/useABTest';
import { useCountUp } from '../../hooks/useCountUp';
import Skeleton from '../ui/Skeleton';

export default function ABTestPanel() {
  const { data, isLoading, isError } = useABTestResults();

  if (isLoading) {
    return (
      <div className="px-6 py-8 overflow-y-auto h-full bg-[#FAFBF9]">
        <h2 className="text-2xl font-medium text-auralis-green mb-6">A/B Test Results</h2>
        <div className="grid grid-cols-2 gap-6 mb-6">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="px-6 py-8 overflow-y-auto h-full bg-[#FAFBF9]">
        <h2 className="text-2xl font-medium text-auralis-green mb-6">A/B Test Results</h2>
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 flex items-center space-x-3">
          <AlertCircle className="w-5 h-5" />
          <span>Failed to load A/B test data.</span>
        </div>
      </div>
    );
  }

  const adaptiveWins = data.adaptive_conversion_rate > data.static_conversion_rate;

  const staticRate = useCountUp(data.static_conversion_rate * 100, 1200, true);
  const adaptiveRate = useCountUp(data.adaptive_conversion_rate * 100, 1200, true);
  const staticSessions = useCountUp(data.sessions_per_variant.STATIC, 1200, true);
  const adaptiveSessions = useCountUp(data.sessions_per_variant.ADAPTIVE, 1200, true);
  const staticConf = useCountUp(data.static_avg_confidence * 100, 1200, true);
  const adaptiveConf = useCountUp(data.adaptive_avg_confidence * 100, 1200, true);
  
  const improvementTarget = data.static_conversion_rate > 0 
    ? (((data.adaptive_conversion_rate - data.static_conversion_rate) / data.static_conversion_rate) * 100)
    : 0;
  const improvement = useCountUp(improvementTarget, 1200, true);

  const chartData = [
    {
      name: 'Conversion Rate',
      STATIC: parseFloat((data.static_conversion_rate * 100).toFixed(1)),
      ADAPTIVE: parseFloat((data.adaptive_conversion_rate * 100).toFixed(1)),
    }
  ];

  const gridVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="px-6 py-8 overflow-y-auto h-full bg-[#FAFBF9]">
      <h2 className="text-2xl font-display font-normal text-auralis-green mb-6 tracking-tight">A/B Test Results</h2>

      {/* Hero Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* STATIC Card */}
        <motion.div 
            variants={itemVariants}
            whileHover={{ y: -2, boxShadow: "0 8px 30px rgba(28,46,30,0.08)" }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
            className={`bg-white border-2 rounded-2xl p-6 relative ${!adaptiveWins ? 'border-auralis-sage' : 'border-[#F1F3F1]'}`}
          >
            {!adaptiveWins && <Crown className="absolute top-6 right-6 w-6 h-6 text-auralis-sage" />}
            <div className="text-xs font-sans font-medium tracking-widest uppercase text-auralis-mist mb-2">STATIC</div>
            <div className="flex items-start text-auralis-green mb-6">
              <span className="text-6xl font-display font-normal tracking-tight">{staticRate.toFixed(1)}</span>
              <span className="text-2xl font-sans font-light text-auralis-mist mt-1">%</span>
            </div>
            
            <div className="grid grid-cols-2 gap-4 border-t border-auralis-frost pt-4">
              <div>
                <div className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-mist mb-1">Sessions</div>
                <div className="text-lg font-display font-normal text-auralis-green">{Math.round(staticSessions)}</div>
              </div>
              <div>
                <div className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-mist mb-1">Avg Confidence</div>
                <div className="text-lg font-display font-normal text-auralis-green">{staticConf.toFixed(0)}%</div>
              </div>
            </div>
          </motion.div>

          {/* ADAPTIVE Card */}
          <motion.div 
            variants={itemVariants}
            whileHover={{ y: -2, boxShadow: "0 8px 30px rgba(28,46,30,0.08)" }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
            className={`bg-white border-2 rounded-2xl p-6 relative ${adaptiveWins ? 'border-auralis-sage' : 'border-[#F1F3F1]'}`}
          >
            {adaptiveWins && <Crown className="absolute top-6 right-6 w-6 h-6 text-auralis-sage" />}
            <div className="text-xs font-sans font-medium tracking-widest uppercase text-auralis-mist mb-2">ADAPTIVE</div>
            <div className="flex items-start text-auralis-green mb-6">
              <span className="text-6xl font-display font-normal tracking-tight">{adaptiveRate.toFixed(1)}</span>
              <span className="text-2xl font-sans font-light text-auralis-mist mt-1">%</span>
            </div>
            
            <div className="grid grid-cols-2 gap-4 border-t border-auralis-frost pt-4">
              <div>
                <div className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-mist mb-1">Sessions</div>
                <div className="text-lg font-display font-normal text-auralis-green">{Math.round(adaptiveSessions)}</div>
              </div>
              <div>
                <div className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-mist mb-1">Avg Confidence</div>
                <div className="text-lg font-display font-normal text-auralis-green">{adaptiveConf.toFixed(0)}%</div>
              </div>
            </div>
          </motion.div>
      </div>

      {/* Improvement Banner */}
      {data.static_conversion_rate > 0 && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
            <div className="bg-auralis-cream rounded-2xl px-6 py-4 flex items-center justify-center space-x-3 text-auralis-sage font-medium">
              <ArrowUpRight className="w-5 h-5" />
              <span>+{improvement.toFixed(1)}% improvement</span>
            </div>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
        {/* Chart */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white border border-auralis-frost rounded-2xl p-6 shadow-sm flex flex-col"
        >
          <h3 className="text-lg font-display font-normal text-auralis-green mb-6">Conversion Comparison</h3>
          <div className="w-full h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#5A635A', fontFamily: 'DM Sans' }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 12, fill: '#5A635A', fontFamily: 'DM Sans' }} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: '#F1F3F1' }} contentStyle={{ borderRadius: '12px', border: '1px solid #EAECE9', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#5A635A', fontFamily: 'DM Sans', paddingTop: '10px' }} />
                <Bar dataKey="STATIC" fill="#D1D5DB" radius={[6, 6, 0, 0]} animationDuration={1500}>
                  <LabelList dataKey="STATIC" position="top" fill="#5A635A" fontSize={12} formatter={(val: any) => `${val}%`} />
                </Bar>
                <Bar dataKey="ADAPTIVE" fill="#4D6D47" radius={[6, 6, 0, 0]} animationDuration={1500}>
                  <LabelList dataKey="ADAPTIVE" position="top" fill="#4D6D47" fontSize={12} fontWeight={500} formatter={(val: any) => `${val}%`} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Detailed Grid */}
        <motion.div 
          variants={gridVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 gap-4"
        >
          {/* STATIC Column */}
          <motion.div variants={itemVariants} className="bg-white border border-auralis-frost rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-sm">
            <p className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-mist mb-1">Static Sessions</p>
            <p className="text-xl font-display font-normal text-auralis-green">{data.sessions_per_variant.STATIC}</p>
          </motion.div>
          
          {/* ADAPTIVE Column */}
          <motion.div variants={itemVariants} className="bg-auralis-cream/50 border border-auralis-sage/20 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-sm">
            <p className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-sage mb-1">Adaptive Sessions</p>
            <p className="text-xl font-display font-normal text-auralis-green">{data.sessions_per_variant.ADAPTIVE}</p>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-white border border-auralis-frost rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-sm">
            <p className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-mist mb-1">Static Conv.</p>
            <p className="text-xl font-display font-normal text-auralis-green">{staticRate}%</p>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-auralis-cream/50 border border-auralis-sage/20 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-sm">
            <p className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-sage mb-1">Adaptive Conv.</p>
            <p className="text-xl font-display font-normal text-auralis-green">{adaptiveRate}%</p>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-white border border-auralis-frost rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-sm">
            <p className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-mist mb-1">Static Conf.</p>
            <p className="text-xl font-display font-normal text-auralis-green">{(data.static_avg_confidence * 100).toFixed(0)}%</p>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-auralis-cream/50 border border-auralis-sage/20 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-sm">
            <p className="text-xs font-sans font-medium uppercase tracking-widest text-auralis-sage mb-1">Adaptive Conf.</p>
            <p className="text-xl font-display font-normal text-auralis-green">{(data.adaptive_avg_confidence * 100).toFixed(0)}%</p>
          </motion.div>
        </motion.div>
      </div>

    </div>
  );
}
