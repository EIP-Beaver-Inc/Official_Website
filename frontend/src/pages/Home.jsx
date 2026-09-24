import Hero from '@/components/home/Hero';
import StatsBand from '@/components/home/StatsBand';
import ScanStory from '@/components/home/ScanStory';
import DefectsSection from '@/components/home/DefectsSection';
import FinalCTA from '@/components/home/FinalCTA';

export default function Home() {
    return (
        <div data-testid="home-page">
            <Hero />
            <StatsBand />
            <ScanStory />
            <DefectsSection />
            <FinalCTA />
        </div>
    );
}
