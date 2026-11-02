import TopBanner from './TopBanner';
import TopNavBar from './TopNavBar';
import Footer    from './Footer';

// Master layout — wraps every page
export default function Layout({ children }) {
  return (
    <div className="dark bg-background text-on-surface min-h-screen selection:bg-primary-container selection:text-on-primary-container overflow-x-hidden antialiased flex flex-col">
      <TopBanner />
      <TopNavBar />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
