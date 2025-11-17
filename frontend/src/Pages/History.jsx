import { useState, useEffect } from "react";
import PPEStatus from "../Components/PPEStatus";

const History = () => {
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAttendance = async () => {
      try {
        const response = await fetch("/api/user/history", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        });
  
        const data = await response.json();
  
        if (response.ok) {
          setAttendance(data);
        } else {
          setError(data.error || "Failed to fetch attendance data.");
        }
      } catch (error) {
        setError(`Error fetching data: ${error.message}`);
      } finally {
        setLoading(false);
      }
    };
  
    fetchAttendance();
  }, []);

  const formatDate = (isoString) => {
    if (!isoString) return "—";
    const currentDate = new Date(isoString)
      .toLocaleDateString("en-US", { timeZone: "Asia/Kolkata", year: 'numeric', month: 'long', day: 'numeric' });
    return currentDate;
  };

  const formatTime = (isoString) => {
    if (!isoString) return "—";
    const date = new Date();
    const [hours, minutes, seconds] = isoString.split(":").map(Number);
    const newDate = new Date(date.getFullYear(), date.getMonth(), date.getDate(), hours, minutes, seconds);
    if (isNaN(newDate.getTime())) return "Invalid Time";
    return newDate.toLocaleTimeString("en-US", {
      timeZone: "Asia/Kolkata",
      hour12: false,
    });
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case "present":
        return "bg-green-100 text-green-800 border-green-200";
      case "late":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "absent":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Attendance History</h1>
        <p className="text-muted-foreground">View your complete attendance records.</p>
      </div>

      {loading ? (
        <div className="rounded-lg border bg-card p-12 text-center">
          <p className="text-muted-foreground">Loading attendance records...</p>
        </div>
      ) : error ? (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4">
          <p className="text-destructive">{error}</p>
        </div>
      ) : (
        <div className="rounded-lg border bg-card shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Date</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Check-In Time</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Check-Out Time</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Status</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">PPE Status</th>
                </tr>
              </thead>
              <tbody>
                {attendance.length > 0 ? (
                  attendance.map((entry, index) => (
                    <tr key={index} className="border-b transition-colors hover:bg-muted/50">
                      <td className="p-4 align-middle">{formatDate(entry.date)}</td>
                      <td className="p-4 align-middle font-mono text-sm">{formatTime(entry.check_in_time)}</td>
                      <td className="p-4 align-middle font-mono text-sm">{entry.check_out_time ? formatTime(entry.check_out_time) : "—"}</td>
                      <td className="p-4 align-middle">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getStatusColor(entry.status)}`}>
                          {entry.status}
                        </span>
                      </td>
                      <td className="p-4 align-middle">
                        <PPEStatus 
                          ppeCompliant={entry.ppe_compliant} 
                          ppeItems={entry.ppe_items_detected}
                          showDetails={true}
                        />
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="p-12 text-center text-muted-foreground">
                      No attendance records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default History;
