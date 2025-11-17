import WelcomeNote from '../Components/WelcomeNote';
import DataTile from '../Components/DataTile';
import CalendarComp from "../Components/CalendarComp";
import UserBar from '../Components/UserBar';

const Dashboard = () => {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here's your attendance overview.</p>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-6">
                <WelcomeNote />
                <DataTile />
              </div>
        <div>
              <CalendarComp />
        </div>
      </div>

      <div>
        <UserBar />
      </div>
    </div>
  )
}

export default Dashboard
