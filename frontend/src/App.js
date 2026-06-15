import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import { useFadeUpObserver } from '@/hooks/useFadeUp';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Home from '@/pages/Home';
import Quiz from '@/pages/Quiz';
import Contact from '@/pages/Contact';
import Beta from '@/pages/Beta';
import BetaDownload from '@/pages/BetaDownload';
import AdminLogin from '@/pages/AdminLogin';
import Admin from '@/pages/Admin';
import NotFound from '@/pages/NotFound';
import '@/App.css';

function Layout({ children }) {
    useFadeUpObserver();
    return (
        <div className="App min-h-screen flex flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
            <Toaster
                position="top-right"
                toastOptions={{
                    classNames: {
                        toast: 'bg-card text-foreground border border-border shadow-lg rounded-xl',
                    },
                }}
            />
        </div>
    );
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route
                    path="/"
                    element={
                        <Layout>
                            <Home />
                        </Layout>
                    }
                />
                <Route
                    path="/quiz"
                    element={
                        <Layout>
                            <Quiz />
                        </Layout>
                    }
                />
                <Route
                    path="/contact"
                    element={
                        <Layout>
                            <Contact />
                        </Layout>
                    }
                />
                <Route
                    path="/beta"
                    element={
                        <Layout>
                            <Beta />
                        </Layout>
                    }
                />
                <Route
                    path="/beta/download"
                    element={
                        <Layout>
                            <BetaDownload />
                        </Layout>
                    }
                />
                <Route path="/admin/login" element={<AdminLogin />} />
                <Route path="/admin" element={<Admin />} />
                <Route
                    path="*"
                    element={
                        <Layout>
                            <NotFound />
                        </Layout>
                    }
                />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
