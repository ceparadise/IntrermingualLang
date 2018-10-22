package org.apache.maven.lifecycle.session.phase;

/* ====================================================================
 *   Copyright 2001-2004 The Apache Software Foundation.
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 * ====================================================================
 */

import org.apache.maven.execution.MavenExecutionRequest;
import org.apache.maven.execution.MavenExecutionResponse;
import org.apache.maven.lifecycle.goal.MavenGoalExecutionContext;
import org.apache.maven.lifecycle.goal.MavenGoalPhaseManager;
import org.apache.maven.lifecycle.session.AbstractMavenSessionPhase;
import org.apache.maven.execution.MavenSession;

import java.util.Iterator;

/**
 * @author <a href="mailto:jason@maven.org">Jason van Zyl </a>
 * @version $Id$
 */
public class GoalExecutionPhase
    extends AbstractMavenSessionPhase
{
    public void execute( MavenExecutionRequest request, MavenExecutionResponse response )
        throws Exception
    {
        MavenSession session = request.getSession();

        MavenGoalPhaseManager lifecycleManager = (MavenGoalPhaseManager) session.lookup( MavenGoalPhaseManager.ROLE );

        for ( Iterator iterator = session.getGoals().iterator(); iterator.hasNext(); )
        {
            String goal = (String) iterator.next();

            MavenGoalExecutionContext context;

            context = new MavenGoalExecutionContext( session, goal );

            context.setGoalName( goal );

            lifecycleManager.execute( context );

            if ( context.isExecutionFailure() )
            {
                response.setExecutionFailure( context.getGoalName(), context.getFailureResponse() );

                break;
            }
        }
    }
}