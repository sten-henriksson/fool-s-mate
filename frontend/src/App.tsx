import {  Route, Switch } from "wouter";
 
import PageHome from "./page_home";
 
import { useState } from "react";
import { useLocation } from "wouter";
 
const App = () => {
  const [searchQuery, setSearchQuery] = useState("");

  const [, setLocation] = useLocation();
 

  return (
  <>
 


    {/* 
      Routes below are matched exclusively -
      the first matched route gets rendered
    */}
      <Switch>
        <Route path="/">
        <PageHome />
        </Route>
      <Route>404: No such page!</Route>
    </Switch>
  </>
  );
}
export default App;
