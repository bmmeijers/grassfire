
public static float ClosestTimeOfApproach(Vector3 pos1, Vector3 vel1, Vector3 pos2, Vector3 vel2)
{
  //float t = 0;
  var dv = vel1 - vel2;
  var dv2 = Vector3.Dot(dv, dv);
  if (dv2 < 0.0000001f)      // the tracks are almost parallel
  {
      return 0.0f; // any time is ok.  Use time 0.
  }
  
  var w0 = pos1 - pos2;
  return (-Vector3.Dot(w0, dv)/dv2);
}

public static float ClosestDistOfApproach(Vector3 pos1, Vector3 vel1, Vector3 pos2, Vector3 vel2, out Vector3 p1, out Vector3 p2)
{
  var t = ClosestTimeOfApproach(pos1,vel1,pos2,vel2);
  p1 = pos1 + (t * vel1);
  p2 = pos2 + (t*vel2);

  return Vector3.Distance(p1, p2);           // distance at CPA
}

public static Vector3 ClosestPointOfApproach(Vector3 pos1, Vector3 vel1, Vector3 pos2, Vector3 vel2)
{
  var t = ClosestTimeOfApproach(pos1, vel1, pos2, vel2);
  if (t<0) // don't detect approach points in the past, only in the future;
  {
      return (pos1); 
  }

  return (pos1 + (t * vel1));
  
}
